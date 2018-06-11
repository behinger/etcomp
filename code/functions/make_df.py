#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:57:55 2018

@author: kgross

GET nice DATAFRAMES

- samples
- epochs
- full

"""
 
import numpy as np
import pandas as pd

import functions.et_helper as  helper


#%% MAKE SAMPLES

def make_samples_df(etsamples):
   
    fields_to_keep = set(['smpl_time', 'gx', 'gy', 'confidence', 'pa',  'type','gx_vel','gy_vel'])
    
    fields_to_fillin = fields_to_keep - set(etsamples.columns)
    fields_to_copy =  fields_to_keep - fields_to_fillin
    
    etsamples_reduced = etsamples.loc[:,fields_to_copy]
    
    for fieldname in fields_to_fillin:
        etsamples_reduced.loc[:,fieldname] = np.nan
    
    # convert pixels into visual degrees
    # VD
    etsamples_reduced.gx = helper.px2deg(etsamples_reduced.gx, 'horizontal')
    etsamples_reduced.gy = helper.px2deg(etsamples_reduced.gy, 'vertical')
    
    return(etsamples_reduced)



def make_events_df(etevents):
    fields_to_keep = set(['blink_id', 'end_time', 'start_time', 'type', 'amplitude', 'duration', 'end_point', 'peak_velocity', 'start_point', 'vector', 'mean_gx', 'mean_gy', 'fix_rms'])
        
    fields_to_fillin = fields_to_keep - set(etevents.columns)
    fields_to_copy =  fields_to_keep - fields_to_fillin
    
    etevents_reduced = etevents.loc[:,fields_to_copy]
    
    for fieldname in fields_to_fillin:
        etevents_reduced.loc[:,fieldname] = np.nan
    
    return(etevents_reduced)
    
#%% MAKE EPOCHS

def make_epochs(et,msgs,td=[-2,2]):
    # formally called match_data

    # Input:    et(DataFrame)      input data of the eyetracker (has column smpl_time)
    #           msgs(DataFrame)    already parsed input messages    e.g. 'GRID element 5 pos-x 123 ...' defining experimental events (has column msg_time)
    # Output:   df for each notification,
    #           find all samples that are in the range of +-td (default timediff 2 s)
    
    epoched_data = pd.DataFrame()
    
    for idx,msg in msgs.iterrows():
        print(idx)
        ix = ((et['smpl_time'] - msg['msg_time'])>td[0]) & ((et['smpl_time'] - msg['msg_time'])<td[1]) # ix is a boolean (0 / 1, false / true) (this way we find all samples +-td)
        if np.sum(ix) == 0:
            print('warning, no sample found for msg %i'%(idx))
            print(msg)
            continue
        tmp= et.loc[ix]
        tmp = tmp.assign(td=tmp.smpl_time-msg['msg_time'])
    
        msg_tmp = pd.concat([msg.to_frame()]*tmp.shape[0],axis=1).T
        msg_tmp.index = tmp.index
                
        tmp = pd.concat([tmp,msg_tmp],axis=1)
        epoched_data = epoched_data.append(tmp)
                 
    return(epoched_data)
 
   
#%% 

def make_large_grid_df(merged_events):
    # Input:    merged_events have info from msgs df AND event df
    #           (see add_msg_to_event in et_helper)
    
    # only large grid condition
    large_grid_events = merged_events.query('condition == "GRID"').loc[:,['type', 'end_time', 'mean_gx','duration', 'start_time', 'fix_rms', 'mean_gy', 'block', 'condition', 'element', 'exp_event', 'grid_size', 'msg_time', 'posx', 'posy']]
    stopevents = large_grid_events.query('exp_event=="stop"').assign(element=50.,grid_size=49.,posx=0,posy=0,exp_event='element')
    large_grid_events.loc[stopevents.index] = stopevents
    # only last fixation before new element
    large_grid_df = helper.only_last_fix(large_grid_events, next_stim = ['block', 'element'])

    
    return large_grid_df