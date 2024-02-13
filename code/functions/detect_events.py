#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 16:42:55 2018


"""
import cateyes
import functions.detect_saccades as saccades
import functions.et_helper as et_helper
import functions.et_make_df as make_df
import logging
import os
import pandas as pd
import numpy as np


def verify_and_filter_blinks(etsamples, etevents=None):
    """
    Detects and verifies blinks in eye tracking samples data. It also removes all non-blink events for an 
    optional events dataframe.
    
    Parameters:
        etsamples (pd.DataFrame): A DataFrame containing eye tracking samples data.
        etevents (pd.DataFrame, optional): A DataFrame containing eye tracking events data. Defaults to None.
    Returns: A tuple containing two elements:
        etsamples (pd.DataFrame): The original `etsamples` DataFrame.
        etevents (pd.DataFrame): The DataFrame containing detected blink events, if `etevents` was provided.
    """

    logger = logging.getLogger(__name__)
    logger.debug('Detecting blinks in samples.')

    if "blink" in etsamples.columns:
        logger.warning("Found 'blink' column in DataFrame.")
    else:
        logger.warning("No 'blink' column in DataFrame.")

    if etevents is not None:
        logger.debug('Eyelink blink events are already in "etevents". Deleting all other eyelink events')
        etevents = etevents.query('blink == True')
        etevents = etevents.rename(columns={'start':'start_time','end':'end_time'})
        etevents['type'] = "blink"
    
    return etsamples, etevents

#%% PL Events df

# def make_blinks(etsamples, etevents, et):
    
#     # get a logger
#     logger = logging.getLogger(__name__)
    
#     if et == 'tpx':
#         logger.debug('Detecting TrackPixx Blinks')
        
#         # add Blink information to pldata
#         etsamples = pl_detect_blinks(etsamples)
#         etsamples['blink_id'] = (1*(etsamples['is_blink']==1)) * ((1*(etsamples['is_blink']==1)).diff()==1).cumsum()

#         blinkevents = pl_make_blink_events(etsamples)        
#         etsamples = etsamples.drop('is_blink',axis=1)
        
#         # etevents is empty
#         etevents= pd.concat([etevents, blinkevents], axis=0,sort=False)
    
#     elif et == 'el':
#         logger.debug('Eyelink blink events are already in "etevents". Deleting all other eyelink events')
        
#         etevents = etevents.query('blink == True')
#         etevents = etevents.rename(columns={'start':'start_time','end':'end_time'})
#         etevents['type'] = "blink"
    
#     return(etsamples, etevents)


def detect_saccades_cateyes(etsamples):
    cl_disp, classes = cateyes.classify_dispersion(etsamples.gx, etsamples.gy, etsamples.smpl_time, 2.,0.1) # 2°, 100ms

    saccades = []
    for idx in np.unique(cl_disp):
        if idx == 0:
            continue
        ix = np.argwhere(cl_disp == idx)
        #etsamples.smpl_time[ix[0]])
        #print(classes[ix[0][0]],ix[0])
        
        if classes[ix[0][0]] != "Saccade":
            continue
                # only velocity based
        
        this_saccade = {
        'start_time': etsamples.smpl_time.iloc[ix[0][0]],
        'end_time': etsamples.smpl_time.iloc[ix[-1][0]],
        'duration': len(ix)/1000,
        'start_gx': etsamples.gx.iloc[ix[0][0]],
        'start_gy': etsamples.gy.iloc[ix[0][0]],
        'end_gx': etsamples.gx.iloc[ix[-1][0]],
        'end_gy': etsamples.gy.iloc[ix[-1][0]],
        }
        saccades.append(this_saccade)
        # no need to calculate the raw_amplitude here as we will calculate the SPHERICAL amplitude later
        #'raw_amplitude': np.sum(normed_vel_data[cis[0]:cis[1]]),
        #'raw_peak_velocity': np.max(normed_vel_data[cis[0]:cis[1]]) * sample_rate,

    saccade_df = pd.DataFrame(saccades)
    saccade_df['amplitude']= saccade_df.apply(lambda localrow:make_df.calc_3d_angle_points(localrow.start_gx,localrow.start_gy,localrow.end_gx,localrow.end_gy),axis=1)
    saccade_df.reset_index()
    return saccade_df


def make_saccades(etsamples, etevents=None, engbert_lambda=5):

    #saccadeevents = saccades.detect_saccades_engbert_mergenthaler(etsamples,etevents,et=et,engbert_lambda=engbert_lambda)

    saccadeevents = detect_saccades_cateyes(etsamples)

    # select only interesting columns: keep only the raw
    #keepcolumns = [s for s in saccadeevents.columns if "raw" in s]
    #saccadeevents = saccadeevents[keepcolumns]
    
    # remove the part of the string that says raw in order to be consistent
    #newname = [s.replace('raw_','') for s in saccadeevents.columns if "raw" in s]
    
    #saccadeevents = saccadeevents.rename(columns=dict(zip(keepcolumns,newname)))
    
    # add the type    
    saccadeevents['type'] = 'saccade'
    
    if etevents is not None:
        # concatenate to original event df
        etevents= pd.concat([etevents, saccadeevents], axis=0,sort=False)
    
    return etsamples, etevents

    
def make_fixations(etsamples, etevents, et):
    from functions.et_helper import winmean
    # this happened already:  
    # etsamples, etevents = make_blinks(etsamples, etevents, et)
    # etsamples, etevents = make_saccades(etsamples, etevents, et)
    
    # get a logger
    logger = logging.getLogger(__name__)
    
    # add labels blink and saccade information from the event df  to sample df
    etsamples = et_helper.add_events_to_samples(etsamples, etevents)
     
    # get all nan index (not a blink neither a saccade) and pupil has to be detected and no negative time
    ix_fix = pd.isnull(etsamples.type) & (etsamples.zero_pa==False)  & (etsamples.neg_time==False)
    # mark them as fixations
    etsamples.loc[ix_fix, 'type'] = 'fixation'
    
    # use magic to get start and end times of fixations in a temporary column
    etsamples.loc[:,'tmp_fix'] = ((1*(etsamples['type'] == 'fixation')).diff())
    etsamples.loc[:,'tmp_fix'].iloc[0] = 0
    etsamples.loc[:,'tmp_fix'] = etsamples['tmp_fix'].astype(int)
    
    # first sample should be fix start?
    if etsamples['tmp_fix'].iloc[np.argmax(etsamples['tmp_fix'] != 0)] == -1:  #argmax stops at first true
        # if we only find an fixation end, add a start at the beginning
        etsamples.iloc[0, etsamples.columns.get_loc('tmp_fix')] = 1
        
    
        
    # make a list of the start and end times
    start_times_list = list(etsamples.loc[etsamples['tmp_fix'] == 1, 'smpl_time'].astype(float))
    end_times_list   = list(etsamples.loc[etsamples['tmp_fix'] == -1, 'smpl_time'].astype(float))
    
    if len(start_times_list) == len(end_times_list)+1:
        # drop the last one if not finished
        start_times_list = start_times_list[0:-1]
        
    # drop the temporary column
    etsamples.drop('tmp_fix', axis=1, inplace=True)
    
    # add them as columns to a fixationevent df
    fixationevents = pd.DataFrame([start_times_list, end_times_list], ['start_time', 'end_time']).T

    # delete event if start or end is NaN
    fixationevents.dropna(subset=['start_time', 'end_time'], inplace=True)

    # add the type    
    
    fixationevents.loc[:,'type'] = 'fixation'
    fixationevents.loc[:,'duration'] = fixationevents['end_time'] - fixationevents['start_time']

    # delete fixationevents shorter than 50 ms
    #logger.warning("Deleted %s fixationsevents of %s fixationsevents in total cause they were shorter than 50ms", np.sum(fixationevents.duration <= 0.05), len(fixationevents))
    #fixationevents = fixationevents[fixationevents.duration > 0.05]
    
    
    for ix,row in fixationevents.iterrows():
        # take the mean gx/gy position over all samples that belong to that fixation
        # removed bad samples explicitly
        ix_fix = (etsamples.smpl_time >= row.start_time) & (etsamples.smpl_time <= row.end_time) & (etsamples.zero_pa==False)  & (etsamples.neg_time==False)
        fixationevents.loc[ix, 'mean_gx'] =  winmean(etsamples.loc[ix_fix, 'gx'])    
        fixationevents.loc[ix, 'mean_gy'] =  winmean(etsamples.loc[ix_fix, 'gy'])

        fix_samples = etsamples.loc[ix_fix,['gx', 'gy']]

        # calculate rms error (inter-sample distances)
       
        if fix_samples.empty:
            logger.error('Empty fixation sample df encountered for fix_event at index %s', ix)

        else:                
            # the thetas are the difference in spherical angle
            fixdf = pd.DataFrame({'x0':fix_samples.iloc[:-1].gx.values,'y0':fix_samples.iloc[:-1].gy.values,'x1':fix_samples.iloc[1:].gx.values,'y1':fix_samples.iloc[1:].gy.values})
            thetas = fixdf.apply(lambda row:make_df.calc_3d_angle_points(row.x0,row.y0,row.x1,row.y1),axis=1)
       
            # calculate the rms
            #print('ix : %s', ix)
            #print('fixdf : %s', len(fixdf))
            #print('np.sqrt((np.square(thetas)).mean()) : %s', np.sqrt((np.square(thetas)).mean()))
            fixationevents.loc[ix, 'rms'] = np.sqrt((np.square(thetas)).mean())
            
            fixdf = pd.DataFrame({'x0':fix_samples.gx.mean(),'y0':fix_samples.gy.mean(),'x1':fix_samples.gx.values,'y1':fix_samples.gy.values})
            thetas = fixdf.apply(lambda row:make_df.calc_3d_angle_points(row.x0,row.y0,row.x1,row.y1),axis=1)
            
            fixationevents.loc[ix, 'sd'] = np.sqrt(np.mean(np.square(thetas)))



    # Sanity checks

    # check if negative duration:
    if (fixationevents.duration < 0).any():
        logger.warning("something is wrong" )    
    
    # concatenate to original event df    
    etevents= pd.concat([etevents, fixationevents], axis=0,sort=False)
     
    return etsamples, etevents

#%%
    
# def pl_make_blink_events(pl_extended_samples):
#     # detects Blink events for pupillabs
    
#     assert('is_blink' in pl_extended_samples)
#     assert('blink_id' in pl_extended_samples)
    
#     # init lists to store info
#     blink_id = []
#     start    = []
#     end      = []
#     #is_blink = []
#     event_type = []
    
#     # for each sample look at the blink_id
#     for int_blink_id in pl_extended_samples.blink_id.unique():
#         # if it is a blink (then the id is not zero)
#         if int_blink_id != 0:
#             # take all samples that the current unique blink_id
#             query = 'blink_id == ' + str(int_blink_id)
#             blink_samples = pl_extended_samples.query(query)
            
#             # append infos from queried samples to lists 
#             # is_blink.append(True)
#             blink_id.append(int_blink_id)
#             # blink starts with first marked sample
#             start.append(blink_samples.iloc[0]['smpl_time'])
#             # blink ends with last marked sample
#             end.append(blink_samples.iloc[-1]['smpl_time'])
#             event_type.append("blink")
            
#     # create df and store collected infos there
#     pl_blink_events = pd.DataFrame({'blink_id': blink_id, 'start_time': start, 'end_time': end, 'type': event_type})
    
#     return pl_blink_events      
     


