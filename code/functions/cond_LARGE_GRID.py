#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 16:57:07 2018

@author:  kgross
"""

import functions.add_path
import os

import pandas as pd
import numpy as np
from plotnine import *
from plotnine.data import *

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.make_df as  make_df


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#%%


# specify subject
subject = 'VP4'

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)

# which et do you want to examine?
etsamples = plsamples
etmsgs = plmsgs
etevents = plevents
# or
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents


#%% LETS try for one subject first

# TODO we loose element 1 when merging
merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time')

# make df for grid condition that only contains one fixation per element
large_grid_df = make_df.make_large_grid_df(merged_events)


     
#%% Plot

# make a df that contains all grid element positions
# all displayed Large Grids are the same
grid_elements = pd.DataFrame(data=[large_grid_df.groupby('element').first()['posx'].values, large_grid_df.groupby('element').first()['posy'].values]).T
grid_elements.columns = ['posx_elem', 'posy_elem']


# with rms
ggplot(grid_elements, aes(x='posx_elem', y='posy_elem', color='posx_elem * posy_elem' )) +\
        geom_point()+\
        geom_point(aes(x='mean_gx', y='mean_gy', size='fix_rms', color='posx * posy'),data = large_grid_df )+\
        facet_wrap('~block')+\
        ggtitle('Large Grid using last fix')
 


# with duration
ggplot(grid_elements, aes(x='posx_elem', y='posy_elem', color='posx_elem * posy_elem' )) +\
        geom_point()+\
        geom_point(aes(x='mean_gx', y='mean_gy', size='duration', color='posx * posy'),data = large_grid_df )+\
        facet_wrap('~block')+\
        ggtitle('Large Grid using last fix')
 


#%% Make a for loop over the foldernames (subjectnames)   and have a list of subjects that we exclude from analysis
#Also loop over the et

 
foldernames = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', '007']
subjectnames = [subject for subject in foldernames if subject not in rejected_subjects]

ets = ['pl', 'el']    



large_grid_df = pd.DataFrame()

for subject in subjectnames:
    for et in ets:
        print(et, subject)
        #make_grid_df()
    
        



#%% Sanity checks

# there should not be any NaN values
if Large_Grid.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')
    
        


        
#%% OLD
        
#%%     
        
#%% LOOK at GRID condition

experiment_start = etmsgs.query('condition=="startingET" & block == 1')

gridstart_time   = etmsgs.query(select + '& element == 1')
gridend_time     = etmsgs.query(select + '& element == 49')
grid_start_end   = pd.Series(sum(zip(gridstart_time.msg_time, gridend_time.msg_time), ()))

experiment_end   = etmsgs.query('condition=="Finished"')

# etevents['block']= pd.cut(etevents.start_time,pd.concat([gridstart_time.msg_time,experiment_end.msg_time]),labels = gridstart_time.block, include_lowest=True, right=True)

labels           = ["beginning"] + list([specifier + str(label) for label in gridstart_time.block for specifier in ('block_','other_')])
etevents['block']= pd.cut(etevents.start_time,pd.concat([experiment_start.msg_time, grid_start_end, experiment_end.msg_time],ignore_index = True),labels = labels, include_lowest=True, right=True)


# plot the mean fixation positions of all fixations during the grid condition
# get indices of event df that are within the time window and that are fixations
ix_grid_fix = (etevents.type == 'fixation')

        
        
        