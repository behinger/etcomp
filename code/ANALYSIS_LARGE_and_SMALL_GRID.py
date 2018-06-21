#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 15:33:10 2018

@author: kgross
"""



import functions.add_path
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.make_df as  make_df
import functions.ANALYSIS_get_condition_df as get_condition_df
from functions.detect_events import make_blinks,make_saccades,make_fixations

import logging

#%% df for all elements that appear in all Grids

# specify which subjects you want to analyze
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', '007', 'log_files', 'surface', 'VP3', 'VP7', 'VP8', 'VP12', 'VP15']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    


# load freeview df for all subjects
complete_all_grids_df= get_condition_df.get_complete_small_large_grid_df(subjectnames, ets)


# Sanity check
# there should not be any NaN values
if complete_all_grids_df.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')




#%% start plotting 

complete_all_grids_df.groupby(['posx', 'posy']).count()


# simple: eyetracker vs  mean accuracy over all blocks
ggplot(complete_all_grids_df, aes(x='factor(et).codes', y='spher_accuracy')) +\
          geom_boxplot() +\
          facet_grid('.~condition')+\
          ggtitle('Spherical accuracy in visual degrees')


# using stat_summary
ggplot(aes(x='factor(et).codes', y='spher_accuracy',color='factor(condition)'), data=complete_all_grids_df.groupby(['et', 'subject','condition']).mean().reset_index(level=['et','subject','condition'])) +\
        geom_point(alpha=0.1,data=complete_all_grids_df,position=position_dodge(width=0.7)) +\
        geom_point(position=position_dodge(width=0.7))+geom_line(aes(group='condition'),position=position_dodge(width=0.7)) +\
        facet_grid('.~subject') + \
        ggtitle('Using stat summary')
#        stat_summary(color='red') +\

 
    
    
#%% Displaying accuracy on grid points

# group data so that we have one fixation observation for each grid point in each block and for each subject and for each eyetracker
grouped_elem_pos = complete_all_grids_df.groupby(['et', 'subject','posx', 'posy', 'condition']).mean().reset_index(level=['et', 'subject','posx', 'posy', 'condition']).drop(columns = ['end_time','start_time','msg_time'])

et = 'el'

# select eye tracker
if et == 'pl':
    et_grouped_elem_pos = grouped_elem_pos.query('et == "pl"')

elif et == 'el':
    et_grouped_elem_pos = grouped_elem_pos.query('et == "el"')


# visualize subjects vs blocks for specific eyetracker
ggplot(aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)'), data= et_grouped_elem_pos) +\
        geom_point() + \
        facet_grid('condition~subject')+\
        ggtitle(str(et) + '  Large Grid: subjects vs conditions')






 
#%% plot that we wanted:


 
complete_all_grids_df["condition"] = complete_all_grids_df["condition"].astype('category')
 
complete_all_grids_df["et"] = complete_all_grids_df["et"].astype('category')


# todo groupby subject
# TODO  this is a stupid way to do so
element_pairs = complete_all_grids_df.query('condition=="SMALLGRID_BEFORE" & block == 1 & subject=="VP2"').loc[:,['posx', 'posy']]
dict_elem = element_pairs.to_dict('list')

here_we_go = complete_all_grids_df.isin(dict_elem)

last = complete_all_grids_df[(here_we_go['posx']==True) & (here_we_go['posy']==True)]

last.query('condition=="GRID" & block == 1 & subject=="VP2"& et=="el"')


ggplot(aes(x='posx', y='posy', color='factor(posx * posy)'), data= last) +\
        geom_point()




# simple: eyetracker vs  mean accuracy over all blocks
ggplot(complete_all_grids_df, aes(x='condition', y='spher_accuracy', fill='et')) +\
          geom_boxplot(alpha=0.7) +\
          geom_point(alpha=0.8,data=complete_all_grids_df.groupby(['et','condition']).median().reset_index(level=['et','condition'])) +\
          ggtitle('Spherical accuracy in visual degrees')
















