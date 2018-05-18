#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 16:42:55 2018


"""
import functions.detect_saccades as saccades
import pandas as pd
import os

# parses SR research EDF data files into pandas df
from pyedfread import edf
from functions.pl_detect_blinks import pupil_detect_blinks

#%% PL Events df

def make_blinks(etsamples,etevents,et):
    if et == 'pl':
        print('Detecting Pupillabs Blinks')
        # add Blink information to pldata
        etsamples = pupil_detect_blinks(etsamples)
        blinkevents = pl_make_blink_events(etsamples)        
        
        # etevents is empty
        etevents= pd.concat([etevents, blinkevents], axis=0)
    
    elif et == 'el':
        print('eyelink blink events are already in etevents')
        print('deleting all other eyelink events')
        
        etevents = etevents.query('blink == True')
        etevents = etevents.rename(columns={'start':'start_time','end':'end_time'})
        etevents['type'] = "blink"
    
    return(etsamples,etevents)

def make_saccades(etsamples,etevents,et):
        
    saccadeevents = saccades.detect_saccades_engbert_mergenthaler(etsamples,etevents,et=et)

    # select only interesting columns

    #keep only the raw
    keepcolumns = [s for s in saccadeevents.columns if "raw" in s]
    saccadeevents = saccadeevents[keepcolumns]
    
    # remove the raw
    newname = [s.replace('raw_','') for s in saccadeevents.columns if "raw" in s]
    
    saccadeevents = saccadeevents.rename(columns=dict(zip(keepcolumns,newname)))
    
    # add the type    
    saccadeevents['type'] = 'saccade'
    
    
    etevents= pd.concat([etevents, saccadeevents], axis=0)
    return(etsamples,etevents)

    
def make_fixations(etsamples,etevents,et):
    print('DId not do anything! ')
    return(etsamples,etevents)
#%%
# TODO for pl: return all events in same format as eyelink
def pl_make_events(plsamples):
    raise ('old')
    
    assert('blink_id' in plsamples)
    assert('is_blink' in plsamples)
    
    pl_blink_events = pl_make_blink_events(plsamples)
    pl_sacc_events  = pl_make_sacc_events(plsamples)
    pl_fix_events   = pl_make_fix_events(plsamples)    
    plevents = pl_blink_events.append(pl_sacc_events, ignore_index=True)
    
    return plevents



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
def pl_make_fix_events(pl_extended_samples):
    # detects Blink events for pupillabs
    
    #return pl_fix_events      
    pass


