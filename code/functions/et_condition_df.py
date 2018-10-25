#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:46:11 2018

@author: kgross
"""

import functions.add_path
import os

import pandas as pd

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.et_make_df as  make_df
from functions.detect_events import make_blinks,make_saccades,make_fixations

import logging



#%% Create complete_condition_df depending on the selected condition for all subjects

def get_condition_df(subjectnames=None, ets=None, data=None, condition=None, **kwargs):
    # make the df for the large GRID for both eyetrackers and all subjects
    # **kwargs for using different prefix i.e. using a different event detection algorithm, see et_preprocess
    
    # get a logger
    logger = logging.getLogger(__name__)
    
    if condition == None:
        raise ValueError('Condition must not be None. Please specify a condition')    
    
    # create df
    complete_condition_df = pd.DataFrame()
    complete_fix_count_df = pd.DataFrame()
    
    if data:
        logger.debug('Data already loaded, just applying transformations')
        ets = data[0].eyetracker.unique()
        subjectnames = data[0].subject.unique()
        
        
    for subject in subjectnames:
        for et in ets:
            logger.info('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject at a time
            if not data:
                etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=True,**kwargs)
            else:
                etsamples,etmsgs,etevents = (d.query("eyetracker=='"+et+"'&subject=='"+subject+"'").drop(["eyetracker","subject"],axis=1) for d in data) 
                    
            if condition in ['LARGE_GRID','LARGE_and_SMALL_GRID','SMOOTHPURSUIT','MICROSACC','SHAKE','TILT']:
                
                # adding the messages to the event df (backward merge)   
                if condition in ['TILT','SHAKE']:
                    etmsgs.loc[:,'element'] = etmsgs.groupby(['block','condition','exp_event']).cumcount()

                merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time', direction='backward')
                 
                if condition == 'LARGE_GRID':
                    # make df for grid condition that only contains ONE fixation per element
                    # (the last fixation before the new element  (used a groupby.last() to achieve that))
                    condition_df = make_df.make_large_grid_df(merged_events)          
                
                elif condition == 'LARGE_and_SMALL_GRID':                   
                    # make df for all grids that only contains ONE fixation per element
                    # (last fixation before the new element is shown)
                    condition_df = make_df.make_all_elements_grid_df(merged_events)                  
                    
                elif condition in ['SHAKE']:
                    condition_df = make_df.make_condition(merged_events,condition=condition)                  
                elif condition == 'TILT':
                    condition_df = merged_events.query('condition=="TILT"')
                else:
                    condition_df = merged_events


            elif condition == 'BLINK':
                merged_events = helper.add_msg_to_event(etevents, etmsgs.query("condition=='BLINK'&(exp_event=='stop'|exp_event=='start')"), timefield = 'start_time', direction='backward')
                condition_df =  merged_events.query("type=='blink'&condition=='BLINK'&exp_event=='start'")
                
            elif condition == 'FREEVIEW':
                # due to experimental trigger bug: FORWARD merge to add msgs to the events
                merged_events = helper.add_msg_to_event(etevents, etmsgs.query('condition=="FREEVIEW"'), timefield = 'start_time', direction='forward')
                
                # freeview df
                condition_df, fix_count_df = make_df.make_freeview_df(merged_events)          
                
                # add a column for eyetracker and subject
                fix_count_df.loc[:,'et'] = et
                fix_count_df.loc[:,'subject'] = subject

                # concatenate to the complete fix_count_df                
                complete_fix_count_df = pd.concat([complete_fix_count_df,fix_count_df])     
        
            else:
                raise ValueError('You must specify an implemented condition.')

            
            # do the stuff that we need to do for all conditions anyways
            # add a column for eyetracker and subject
            if condition_df.empty:
                logger.critical('empty subject:%s,et:%s'%(subject,et))
                continue
            condition_df.loc[:,'et'] = et
            condition_df.loc[:,'eyetracker'] = et # behinger added this to keep same as etsamples/etmsgs/etevents. 'et' is later renamed
            condition_df.loc[:,'subject'] = subject
            
            # concatenate the df of one specific conditin and one specific subject to the complete_condition_df
            complete_condition_df = pd.concat([complete_condition_df, condition_df])
 
    
    # set variables to correct dtypes (e.g. from object to categorical)
    # and use full names e.g. el changes to EyeLink 
    complete_condition_df = helper.set_dtypes(complete_condition_df)
    
    # renaming for pretty plotting
    complete_condition_df = helper.set_to_full_names(complete_condition_df)

    
    # Sanity check
    # there must not be any NaN values
    # last time rms caused problems
#    if complete_condition_df.isnull().values.any():
#       logger.error((complete_condition_df.columns[complete_condition_df.isna().any()].tolist()))
#       logger.error((complete_condition_df.rms.mean()))
#       raise ValueError('Some value(s) of the df is NaN')

    
    # TODO: maybe smarter option to write own function for getting the fix_count_df???    ------> later
    # for the freeview condition we return 2 dfs
    if condition == 'FREEVIEW':
        # renaming for pretty plotting
        complete_fix_count_df = helper.set_to_full_names(complete_fix_count_df)
        return complete_condition_df, complete_fix_count_df
    
    # for all other condtions we return the complete_condition_df
    else:
        return complete_condition_df