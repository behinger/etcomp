#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:45:09 2018

@author: kgross
"""


def get_complete_freeview_df(subjectnames, ets):
    # make the df for the large GRID for both eyetrackers and all subjects
    
    # create df
    complete_freeview_df = pd.DataFrame()
    complete_fix_count_df = pd.DataFrame()
        
    for subject in subjectnames:
        for et in ets:
            logging.critical('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=True)
            
            
            # due to experimental triggers: FORWARD merge to add msgs to the events
            merged_events = helper.add_msg_to_event(etevents, etmsgs.query('condition=="FREEVIEW"'), timefield = 'start_time', direction='forward')
            
            # make df for grid condition that only contains ONE fixation per element
            # (the last fixation before the new element  (used a groupby.last() to achieve that))
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
