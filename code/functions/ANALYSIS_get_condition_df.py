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
import functions.make_df as  make_df
from functions.detect_events import make_blinks,make_saccades,make_fixations

import logging


#%% Create large_grid_df for all subjects


def get_complete_large_grid_df(subjectnames, ets):
    # make the df for the large GRID for both eyetrackers and all subjects
    
    # create df
    complete_large_grid_df = pd.DataFrame()
        
    for subject in subjectnames:
        for et in ets:
            logging.critical('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=True)
            
            # adding the messages to the event df
            merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time', direction='backward')
                       
            # make df for grid condition that only contains ONE fixation per element
            # (the last fixation before the new element  (used a groupby.last() to achieve that))
            large_grid_df = make_df.make_large_grid_df(merged_events)          
            
            # add a column for eyetracker and subject
            large_grid_df['et'] = et
            large_grid_df['subject'] = subject
            
            # concatenate to the complete df
            complete_large_grid_df = pd.concat([complete_large_grid_df,large_grid_df])
                   
    return complete_large_grid_df




#%% Create small_large_grid_df for all subjects


def get_complete_small_large_grid_df(subjectnames, ets):
    # make the df for all elements that appear in the small AND the large GRID for both eyetrackers and all subjects
    
    # create df
    complete_small_large_grid_df = pd.DataFrame()
        
    for subject in subjectnames:
        for et in ets:
            logging.critical('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=True)
            
            # adding the messages to the event df
            merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time', direction='backward')
                       
            # make df for grid condition that only contains ONE fixation per element
            # (the last fixation before the new element  (used a groupby.last() to achieve that))
            all_elements_df = make_df.make_all_elements_grid_df(merged_events)          
            
            # add a column for eyetracker and subject
            all_elements_df['et'] = et
            all_elements_df['subject'] = subject
            
            # concatenate to the complete df
            complete_small_large_grid_df = pd.concat([complete_small_large_grid_df,all_elements_df])
                   
    return complete_small_large_grid_df






#%% Create complete_freeview_df for all subjects



def get_complete_freeview_df(subjectnames, ets):
    # make the df for the large GRID for both eyetrackers and all subjects
    
    # create df
    complete_freeview_df = pd.DataFrame()
    complete_fix_count_df = pd.DataFrame()
        
    for subject in subjectnames:
        for et in ets:
            logging.critical('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject, load=True)
            
            
            # due to experimental triggers: FORWARD merge to add msgs to the events
            merged_events = helper.add_msg_to_event(etevents, etmsgs.query('condition=="FREEVIEW"'), timefield = 'start_time', direction='forward')
            
            # freeview df
            freeview_df, fix_count_df = make_df.make_freeview_df(merged_events)          
            
            # add a column for eyetracker and subject
            freeview_df['et'] = et
            fix_count_df['et'] = et
            freeview_df['subject'] = subject
            fix_count_df['subject'] = subject
            
            # concatenate to the complete dfs
            complete_freeview_df = pd.concat([complete_freeview_df,freeview_df])
            complete_fix_count_df = pd.concat([complete_fix_count_df,fix_count_df])
            
            
    return complete_freeview_df, complete_fix_count_df

