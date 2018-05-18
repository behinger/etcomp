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


#%% MAKE SAMPLES

def make_samples_df(etsamples):
    # function to check if all needed columns exist and get samples df
    assert('pa' in etsamples)
    
    fields_to_keep = set(['smpl_time', 'gx', 'gy', 'confidence', 'pa',  'type','gx_vel','gy_vel'])
    
    fields_to_fillin = fields_to_keep - set(etsamples.columns)
    fields_to_copy =  fields_to_keep - fields_to_fillin
    
    etsamples_reduced = etsamples.loc[:,fields_to_copy]
    
    for fieldname in fields_to_fillin:
        etsamples_reduced.loc[:,fieldname] = np.nan
    
    return(etsamples_reduced)



   
#TODO  select only interesting columns
#def make_events_df(etevents)
#elevents = elevents.loc[:, ['start', 'end', 'type']]
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
# FULL df
# TODO
def make_full_df(etmsgs, etevents, condition):
    # Input:
    # Output:    
    full_df = pd.DataFrame()
    # search for start message of condition in **etmsgs**
    
    # search for first saccade / fixation / blink after msg_time in **etevents**
    
    return full_df
