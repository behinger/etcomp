#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 16:42:55 2018


"""
import functions.detect_saccades as saccades
import functions.et_helper as et_helper
import pandas as pd
import numpy as np
import os

# parses SR research EDF data files into pandas df
from pyedfread import edf
from functions.pl_detect_blinks import pl_detect_blinks
from sklearn.metrics import mean_squared_error

#%% PL Events df

def make_blinks(etsamples,etevents,et):
    if et == 'pl':
        print('Detecting Pupillabs Blinks')
        # add Blink information to pldata

        etsamples = pl_detect_blinks(etsamples)
        etsamples['blink_id'] = (1*(etsamples['is_blink']==1)) * ((1*(etsamples['is_blink']==1)).diff()==1).cumsum()

        blinkevents = pl_make_blink_events(etsamples)        
        etsamples = etsamples.drop('is_blink',axis=1)
        
        # etevents is empty
        etevents= pd.concat([etevents, blinkevents], axis=0,sort=False)
    
    elif et == 'el':
        print('eyelink blink events are already in etevents')
        print('deleting all other eyelink events')
        
        etevents = etevents.query('blink == True')
        etevents = etevents.rename(columns={'start':'start_time','end':'end_time'})
        etevents['type'] = "blink"
    
    return(etsamples,etevents)



def make_saccades(etsamples,etevents,et):
    #TODO hier laeuft was falsch!   thresholds anpassen!    
    saccadeevents = saccades.detect_saccades_engbert_mergenthaler(etsamples,etevents,et=et)

    # select only interesting columns: keep only the raw
    keepcolumns = [s for s in saccadeevents.columns if "raw" in s]
    saccadeevents = saccadeevents[keepcolumns]
    
    # remove the part of the string that says raw in order to be consistent
    newname = [s.replace('raw_','') for s in saccadeevents.columns if "raw" in s]
    
    saccadeevents = saccadeevents.rename(columns=dict(zip(keepcolumns,newname)))
    
    # add the type    
    saccadeevents['type'] = 'saccade'
    
    # concatenate to original event df
    etevents= pd.concat([etevents, saccadeevents], axis=0,sort=False)
    
    return etsamples, etevents

    
def make_fixations(etsamples, etevents,et):
    # this happened already:  
    # etsamples, etevents = make_blinks(etsamples, etevents, et)
    # etsamples, etevents = make_saccades(etsamples, etevents, et)
       
    # add labels blink and saccade information from the event df  to sample df
    etsamples = et_helper.add_events_to_samples(etsamples, etevents)
     
    # get all nan index (not a blink neither a saccade)
    ix_fix = pd.isnull(etsamples.type)
    # mark them as fixations
    etsamples.loc[ix_fix, 'type'] = 'fixation'
    
    # TODO: chack and write comments
    # use magic to get start and end times of fixations in a temporary column
    etsamples['tmp_fix'] = ((1*(etsamples['type'] == 'fixation')).diff())
    # assume that we always start with a fixation
    etsamples.iloc[0, etsamples.columns.get_loc('tmp_fix')] = 1
    etsamples['tmp_fix'] = etsamples['tmp_fix'].astype(int)
        
    # make a list of the start and end times
    start_times_list = list(etsamples.loc[etsamples['tmp_fix'] == 1, 'smpl_time'].astype(float))
    end_times_list   = list(etsamples.loc[etsamples['tmp_fix'] == -1, 'smpl_time'].astype(float))
    
    # drop the temporary column
    etsamples.drop('tmp_fix', axis=1, inplace=True)
    
    # add them as columns to a fixationevent df
    fixationevents = pd.DataFrame([start_times_list, end_times_list], ['start_time', 'end_time']).T

    # delete event if start or end is NaN
    fixationevents.dropna(subset=['start_time', 'end_time'], inplace=True)

    # add the type    
    fixationevents['type'] = 'fixation'
    fixationevents['duration'] = fixationevents['end_time'] - fixationevents['start_time']
    
    for ix,row in fixationevents.iterrows():
        # TODO: check could we make thatfaster somehow?
        # take the mean gx/gy position over all samples that belong to that fixation
        # removed bad samples explicitly
        ix_fix = (etsamples.smpl_time >= row.start_time) & (etsamples.smpl_time <= row.end_time) & (etsamples.outside==False) & (etsamples.zero_pa==False)  & (etsamples.neg_time==False)
        fixationevents.loc[ix, 'mean_gx'] =  np.mean(etsamples.loc[ix_fix, 'gx'])    
        fixationevents.loc[ix, 'mean_gy'] =  np.mean(etsamples.loc[ix_fix, 'gy'])
        # TODO calculate rms error
        # do i have to use a for loop here?
#        for sample_ix in ix_fix:
#            x_y   = (etsamples.loc[sample_ix, 'gx'], etsamples.loc[sample_ix, 'gy'])
#            x_y_1 = (etsamples.loc[sample_ix + 1, 'gx'], etsamples.loc[sample_ix + 1, 'gy'])
#            rms   = np.sqrt(((x_y - x_y_1) ** 2).mean())
#        fixationevents.loc[ix, 'fix_rms'] = rms


    # Sanity checks
    # check if negative duration:
    if (fixationevents.duration < 0).any():
        print("something is wrong" )    
    # TODO : check for short fixation durations
    if (fixationevents.duration < 0.1).any():
        print("There are some really short fixations" )
    
    
    # concatenate to original event df    
    etevents= pd.concat([etevents, fixationevents], axis=0,sort=False)
     
    return etsamples, etevents

#%%
    
#    
## TODO for pl: return all events in same format as eyelink
#def pl_make_events(plsamples):
#    raise ('old')
#    
#    assert('blink_id' in plsamples)
#    assert('is_blink' in plsamples)
#    
#    pl_blink_events = pl_make_blink_events(plsamples)
#    pl_sacc_events  = pl_make_sacc_events(plsamples)
#    pl_fix_events   = pl_make_fix_events(plsamples)    
#    plevents = pl_blink_events.append(pl_sacc_events, ignore_index=True)
#    
#    return plevents
#


def pl_make_blink_events(pl_extended_samples):
    # detects Blink events for pupillabs
    
    assert('is_blink' in pl_extended_samples)
    assert('blink_id' in pl_extended_samples)
    
    # init lists to store info
    blink_id = []
    start    = []
    end      = []
    #is_blink = []
    event_type = []
    
    # for each sample look at the blink_id
    for int_blink_id in pl_extended_samples.blink_id.unique():
        # if it is a blink (then the id is not zero)
        if int_blink_id != 0:
            # take all samples that the current unique blink_id
            query = 'blink_id == ' + str(int_blink_id)
            blink_samples = pl_extended_samples.query(query)
            
            # append infos from queried samples to lists 
            # is_blink.append(True)
            blink_id.append(int_blink_id)
            # blink starts with first marked sample
            start.append(blink_samples.iloc[0]['smpl_time'])
            # blink ends with last marked sample
            end.append(blink_samples.iloc[-1]['smpl_time'])
            event_type.append("blink")
            
    # create df and store collected infos there
    pl_blink_events = pd.DataFrame({'blink_id': blink_id, 'start_time': start, 'end_time': end, 'type': event_type})
    
    return pl_blink_events      
     

#TODO
#def pl_make_fix_events(pl_extended_samples):
#    # detects Blink events for pupillabs
#    
#    #return pl_fix_events      
#    pass
#

