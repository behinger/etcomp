#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 18:59:38 2018

@author: kgross
"""


import functions.add_path
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *
# specify costumed minimal theme
import functions.plotnine_theme

import functions.et_helper as  helper
import functions.ANALYSIS_get_condition_df as get_condition_df

import logging


#%% visualize accuracy and precision in LARGE GRID condition


# specify which subjects you want to analyze
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP15', 'VP12', 'VP21', 'VP22']
# rejected_subjects = ['pilot', '007', 'log_files', 'surface', 'VP3', 'VP7', 'VP8', 'VP12', 'VP15']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    

# load grid df for all subjects
complete_large_grid_df = get_condition_df.get_complete_large_grid_df(subjectnames, ets)


# Sanity check
# there should not be any NaN values
if complete_large_grid_df.isnull().values.any():
    logging.error((complete_large_grid_df.columns[complete_large_grid_df.isna().any()].tolist()))
    raise ValueError('Some value(s) of the df is NaN')
    
   


# get df grouped by et and subject 
# take the mean of the accuracy and precision measures over all blocks
grouped_large_grid_df = complete_large_grid_df.groupby(['et', 'subject']).mean().loc[:,['accuracy', 'hori_accuracy', 'vert_accuracy','spher_fix_rms']]
grouped_large_grid_df.reset_index(level=['et', 'subject'], inplace=True)


complete_large_grid_df[complete_large_grid_df.select_dtypes(['object']).columns] = complete_large_grid_df.select_dtypes(['object']).apply(lambda x: x.astype('category'))
grouped_large_grid_df[grouped_large_grid_df.select_dtypes(['object']).columns] = grouped_large_grid_df.select_dtypes(['object']).apply(lambda x: x.astype('category'))



#%% PLOTS
# Making plots for all subjects


# simple: eyetracker vs  mean accuracy over all blocks
ggplot(grouped_large_grid_df, aes(x='et', y='accuracy', color='subject')) +\
          geom_line(aes(group='subject')) +\
          geom_point() +\
          guides(color=guide_legend(ncol=40)) +\
          ggtitle('Spherical accuracy in visual degrees')


# make facets over subjects
# investigate how mean accuracy is changes for different subjects
ggplot(grouped_large_grid_df, aes(x='et', y='accuracy', color='subject')) +\
          geom_line(aes(group='subject')) +\
          geom_point() +\
          guides(color=guide_legend(ncol=40)) +\
          facet_grid('.~subject')+\
          ggtitle('Spherical accuracy in visual degrees')


# using stat_summary
complete_large_grid_df["block"] = complete_large_grid_df["block"].astype('category')

# Here: Learn how to use stat summary          
ggplot(aes(x='et', y='accuracy',color='block'), data=complete_large_grid_df.groupby(['et', 'subject','block']).mean().reset_index(level=['et','subject','block'])) +\
        geom_point(alpha=0.1,data=complete_large_grid_df,position=position_dodge(width=0.7)) +\
        geom_point(position=position_dodge(width=0.7))+geom_line(aes(group='block'),position=position_dodge(width=0.7)) +\
        facet_grid('.~subject') + \
        guides(color=guide_legend(ncol=40)) +\
        ggtitle('Using stat summary')


# just calculating the mean:
# TODO: how can this be different for complete and grouped??
complete_large_grid_df.query('et == "pl"').accuracy.mean()
complete_large_grid_df.query('et == "el"').accuracy.mean()


# using boxplot
ggplot(grouped_large_grid_df, aes(x='et', y='accuracy')) +\
        geom_boxplot() +\
        ggtitle('Mean spherical accuracy over all blocks for each subject')



   
#%% comparing different MEASURES
   
# use melt to investigate on different measures
melted_measures = grouped_large_grid_df.melt(id_vars=['et', 'subject'], var_name='measure')
melted_measures[melted_measures.select_dtypes(['object']).columns] = melted_measures.select_dtypes(['object']).apply(lambda x: x.astype('category'))

# compare accuracy and precision measure (mean over all blocks) for each subject 
ggplot(melted_measures, aes(x='et', y='value', color='measure')) +\
          geom_line(aes(group='measure')) +\
          geom_point() +\
          guides(color=guide_legend(ncol=40)) +\
          facet_grid('.~subject')+\
          ggtitle('Investigating on performance measures (mean over all blocks)')


   
#%% Displaying accuracy on grid points

# group data so that we have one fixation observation for each grid point in each block and for each subject and for each eyetracker
grouped_elem_pos = complete_large_grid_df.groupby(['et', 'subject','posx', 'posy', 'block']).mean().reset_index(level=['et', 'subject','posx', 'posy', 'block']).drop(columns = ['end_time','start_time','msg_time'])

et = 'pl'

# select eye tracker
if et == 'pl':
    et_grouped_elem_pos = grouped_elem_pos.query('et == "pl"')

elif et == 'el':
    et_grouped_elem_pos = grouped_elem_pos.query('et == "el"')


# visualize subjects vs blocks for specific eyetracker
ggplot(aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)'), data= et_grouped_elem_pos) +\
        geom_point() + \
        guides(color=guide_legend(ncol=40)) +\
        facet_grid('block~subject')+\
        ggtitle(str(et) + '  Large Grid: subjects vs block')


# look which grid points by trend have higher/lower accuracy 

# sphere_accuracy
ggplot(aes(x='posx', y='posy', size='accuracy'), data=et_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +\
        geom_point() +\
        facet_wrap('~subject')+\
        ggtitle(str(et) +' accuracy visiualized by size of grid points')


# rms
ggplot(aes(x='posx', y='posy', size='spher_fix_rms'), data=et_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +\
        geom_point() +\
        facet_wrap('~subject')+\
        ggtitle(str(et) +' precision visiualized by size of grid points')







#%% PLOTS for only a specific subject


# Looking at only one subject
specific_subject_df = complete_large_grid_df.query('et == "el" & subject == "VP1" & block == 1')
        
# mean_fix vs grid point elements
ggplot(specific_subject_df, aes(x='mean_gx', y='mean_gy', color='factor(posx*posy)')) \
        + geom_point(alpha=0.3) \
        + geom_point(specific_subject_df, aes(x='posx', y='posy', color='factor(posx*posy)'), alpha=1.0) \
        + ggtitle('Mean fixation gaze vs displayed element points')



#%% SAVE the plot in repository
 
plotname = 'GRID_' + et + '_' + subject

gridplot.save(filename=plotname, format=None, path='/net/store/nbp/users/kgross/etcomp/plots', dpi=600, verbose=True)




