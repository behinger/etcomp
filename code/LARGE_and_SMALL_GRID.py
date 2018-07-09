#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 15:33:10 2018

@author: kgross
"""



import functions.add_path
import os

import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *
# specify costumed minimal theme
import functions.plotnine_theme

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.make_df as  make_df
import functions.ANALYSIS_get_condition_df as get_condition_df
from functions.detect_events import make_blinks,make_saccades,make_fixations

import logging

    

#%% df for all elements that appear in all Grids

# specify which subjects you want to analyze
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
# rejected_subjects = ['pilot', '007', 'log_files', 'surface', 'VP3', 'VP7', 'VP8', 'VP12', 'VP15']
rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP15', 'VP12']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    


# load freeview df for all subjects
complete_all_grids_df= get_condition_df.get_complete_small_large_grid_df(subjectnames, ets)


# Sanity check
# there should not be any NaN values
if complete_all_grids_df.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')


# convert dtypes (object to categorical)
complete_all_grids_df[complete_all_grids_df.select_dtypes(['object']).columns] = complete_all_grids_df.select_dtypes(['object']).apply(lambda x: x.astype('category'))



#%% start plotting 

# simple: eyetracker vs  mean accuracy over all blocks
ggplot(complete_all_grids_df, aes(x='et', y='spher_accuracy')) +\
          geom_boxplot() +\
          facet_grid('.~condition')+\
          ggtitle('Spherical accuracy in visual degrees')


# TODO Rearrange columns for better readability in temporal order of the experiment          
# Determine order and create a categorical type
condition_list = complete_all_grids_df['condition'].value_counts().index.tolist()
condition_list_sorted = ['GRID', 'SMALLGRID_BEFORE', 'SMALLGRID_AFTER']
if not set(condition_list).issubset(set(condition_list_sorted)) :
    raise ValueError('are you sure evrything is okay with the condition reordering?')
    
condition_cat = CategoricalDtype(categories=condition_list_sorted, ordered=True)

# Cast the existing categories into the new category. Due to a bug in pandas we need to do this via a string.
complete_all_grids_df['condition'] = complete_all_grids_df['condition'].astype(str).astype(condition_cat)


# TODO using stat_summary
ggplot(aes(x='et', y='spher_accuracy',color='condition'), data=complete_all_grids_df.groupby(['et', 'subject','condition']).mean().reset_index(level=['et','subject','condition'])) +\
        geom_point(alpha=0.1,data=complete_all_grids_df, position=position_dodge(width=0.7)) +\
        geom_point(position=position_dodge(width=0.7))+geom_line(aes(group='condition'),position=position_dodge(width=0.7)) +\
        facet_grid('.~subject') + \
        ggtitle('Comparing accuracy of conditions')


# points show mean over block for each subject
ggplot(aes(x='et', y='spher_accuracy',color='condition'), data=complete_all_grids_df.groupby(['et', 'subject','condition']).mean().reset_index(level=['et','subject','condition'])) +\
        geom_point(alpha=0.1,data=complete_all_grids_df.groupby(['et', 'subject','condition','block']).mean().reset_index(level=['et','subject','condition','block']),position=position_dodge(width=0.7)) +\
        geom_point(position=position_dodge(width=0.7))+geom_line(aes(group='condition'),position=position_dodge(width=0.7)) +\
        facet_grid('.~subject') + \
        ggtitle('Comparing accuracy of conditions')





    
#%% Displaying accuracy on grid points

# group data so that we have one fixation observation for each grid point in each block and for each subject and for each eyetracker
grouped_elem_pos = complete_all_grids_df.groupby(['et', 'subject','posx', 'posy', 'condition']).mean().reset_index(level=['et', 'subject','posx', 'posy', 'condition']).drop(columns = ['end_time','start_time','msg_time'])

et = 'el'

# select eye tracker
if et == 'pl':
    et_grouped_elem_pos = grouped_elem_pos.query('et == "pl"')

elif et == 'el':
    et_grouped_elem_pos = grouped_elem_pos.query('et == "el"')


# visualize subjects vs conditions for specific eyetracker
ggplot(aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)'), data= et_grouped_elem_pos) +\
        geom_point() + \
        guides(color=guide_legend(ncol=40)) +\
        facet_grid('condition~subject')+\
        ggtitle(str(et) + '  Large Grid: subjects vs conditions')



 
#%% plot that we wanted: See "Schmierzettel"

complete_all_grids_df["condition"] = complete_all_grids_df["condition"].astype('category')
complete_all_grids_df["et"] = complete_all_grids_df["et"].astype('category')


# Get the x and y position of the 13 elements shown in the small Grid condition
element_pairs = complete_all_grids_df.query('condition=="SMALLGRID_BEFORE"').loc[:,['posx', 'posy']]
only_13 = pd.merge(complete_all_grids_df, element_pairs, on=['posx', 'posy'], how='inner')


# look at small Grid
ggplot(aes(x='posx', y='posy', color='factor(posx * posy)'), data= only_13) +\
        geom_point()



# simple: eyetracker vs  mean accuracy over all blocks
ggplot(complete_all_grids_df.groupby(['et', 'subject','condition']).median().reset_index(level=['et', 'subject','condition']), aes(x='condition', y='spher_accuracy', fill='et')) +\
          geom_boxplot(alpha=0.7) +\
          ggtitle('Spherical accuracy in visual degrees')












