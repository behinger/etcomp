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
import functions.et_condition_df as condition_df

import logging



#%% different functions for analysing the Large Grid


def mean_accuracy_by_et_and_subject(raw_large_grid_df):
    """
    groupby
    """
    # get df grouped by et and subject 
    # take the mean of the accuracy and precision measures over all blocks
    mean_over_all_blocks_large_grid_df = raw_large_grid_df.groupby(['Eye-Tracker', 'subject']).mean().loc[:,['accuracy', 'hori_accuracy', 'vert_accuracy','rms']]
    mean_over_all_blocks_large_grid_df.reset_index(level=['Eye-Tracker', 'subject'], inplace=True)
    
    
    return mean_over_all_blocks_large_grid_df



def plot_accuracy(raw_large_grid_df, facets=None):
    """
    Input:   subjectnames (list)
            ets (list) currently aslways: [el, pl]
            facets: None, 'subjects', 
    Output:  ? figure(s) that visualize the difference in accuracy btw. el and pl
    """
    # get data grouped
    mean_over_all_blocks_large_grid_df = mean_accuracy_by_et_and_subject(raw_large_grid_df)
    
    if facets == None:
        # plot eyetracker vs  mean accuracy over all blocks
        (ggplot(mean_over_all_blocks_large_grid_df, aes(x='Eye-Tracker', y='accuracy', color='subject')) +\
                  geom_line(aes(group='subject')) +\
                  geom_point() +\
                  guides(color=guide_legend(ncol=40)) +\
                  ggtitle('Mean spherical accuracy in visual degrees over all blocks for each subject')).draw()
        
    elif facets == 'subjects':
        # make facets over subjects
        # investigate how mean accuracy is changes for different subjects
        (ggplot(mean_over_all_blocks_large_grid_df, aes(x='Eye-Tracker', y='accuracy', color='subject')) +\
                  geom_line(aes(group='subject')) +\
                  geom_point() +\
                  guides(color=guide_legend(ncol=40)) +\
                  facet_grid('.~subject')+\
                  ggtitle('Spherical accuracy in visual degrees')).draw()
        
        
    elif facets == 'dodge':
        # TODO: polish
        # Here: Learn how to use stat summary          
        (ggplot(aes(x='Eye-Tracker', y='accuracy',color='block'), data=raw_large_grid_df.groupby(['Eye-Tracker', 'subject','block']).mean().reset_index(level=['Eye-Tracker','subject','block'])) +\
                geom_point(alpha=0.1,data=raw_large_grid_df,position=position_dodge(width=0.7)) +\
                geom_point(position=position_dodge(width=0.7))+geom_line(aes(group='block'),position=position_dodge(width=0.7)) +\
                facet_grid('.~subject') + \
                guides(color=guide_legend(ncol=40)) +\
                ggtitle('Using stat summary')).draw()


    else:
        raise ValueError('You must set facets to a valid option. See documentation.')



def make_table_accuracy(subjectnames, ets):
    """
    returns a df with all calculated accuracy values
    """
    
    acccuracy_table = pd.DataFrame()
    
    # just calculating the mean:
    # TODO: how can this be different for complete and grouped??
    
    # load grid df for subjectnames
    raw_large_grid_df = condition_df.get_condition_df(subjectnames, ets, condition='LARGE_GRID')
   
    raw_large_grid_df.query('Eye-Tracker == "pl"').accuracy.mean()
    raw_large_grid_df.query('Eye-Tracker == "el"').accuracy.mean()

    
    return acccuracy_table




def compare_accuracy_components(raw_large_grid_df):
    """
    comparing horizontal, vertical and combined spherical agnle accuracy
    """
    
    # get data grouped
    mean_over_all_blocks_large_grid_df = mean_accuracy_by_et_and_subject(raw_large_grid_df)
    
    # use melt to investigate on different components
    melted_measures = mean_over_all_blocks_large_grid_df.melt(id_vars=['Eye-Tracker', 'subject'], var_name='measure')
    
    # compare accuracy and precision measure (mean over all blocks) for each subject 
    (ggplot(melted_measures, aes(x='Eye-Tracker', y='value', color='measure')) +\
              geom_line(aes(group='measure')) +\
              geom_point() +\
              guides(color=guide_legend(ncol=40)) +\
              facet_grid('.~subject')+\
              ggtitle('Investigating on performance measures (mean over all blocks)')).draw()
    
#
#   
##%% Displaying accuracy on grid points
#
## group data so that we have one fixation observation for each grid point in each block and for each subject and for each eyetracker
#grouped_elem_pos = complete_large_grid_df.groupby(['et', 'subject','posx', 'posy', 'block']).mean().reset_index(level=['et', 'subject','posx', 'posy', 'block']).drop(columns = ['end_time','start_time','msg_time'])
#
#et = 'pl'
#
## select eye tracker
#if et == 'pl':
#    et_grouped_elem_pos = grouped_elem_pos.query('et == "pl"')
#
#elif et == 'el':
#    et_grouped_elem_pos = grouped_elem_pos.query('et == "el"')
#
#
## visualize subjects vs blocks for specific eyetracker
#ggplot(aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)'), data= et_grouped_elem_pos) +\
#        geom_point() + \
#        guides(color=guide_legend(ncol=40)) +\
#        facet_grid('block~subject')+\
#        ggtitle(str(et) + '  Large Grid: subjects vs block')
#
#
## look which grid points by trend have higher/lower accuracy 
#
## spherical accuracy
#ggplot(aes(x='posx', y='posy', size='accuracy'), data=et_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +\
#        geom_point() +\
#        facet_wrap('~subject')+\
#        ggtitle(str(et) +' accuracy visiualized by size of grid points')
#
#
## rms
#ggplot(aes(x='posx', y='posy', size='rms'), data=et_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +\
#        geom_point() +\
#        facet_wrap('~subject')+\
#        ggtitle(str(et) +' precision visiualized by size of grid points')
#
#
#
#
#
#
#
##%% PLOTS for only a specific subject
#
#
## Looking at only one subject
#specific_subject_df = complete_large_grid_df.query('et == "el" & subject == "VP1" & block == 1')
#        
## mean_fix vs grid point elements
#ggplot(specific_subject_df, aes(x='mean_gx', y='mean_gy', color='factor(posx*posy)')) \
#        + geom_point(alpha=0.3) \
#        + geom_point(specific_subject_df, aes(x='posx', y='posy', color='factor(posx*posy)'), alpha=1.0) \
#        + ggtitle('Mean fixation gaze vs displayed element points')
#
#
#
##%% SAVE the plot in repository
## TODO: make this more universal and move it to et_helper
#
#plotname = 'GRID_' + et + '_' + subject
#gridplot.save(filename=plotname, format=None, path='/net/store/nbp/users/kgross/etcomp/plots', dpi=600, verbose=True)
#
#


