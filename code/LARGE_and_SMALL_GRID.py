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
import functions.et_make_df as  make_df
import functions.et_condition_df as condition_df
from functions.detect_events import make_blinks,make_saccades,make_fixations



#%% different functions for analysing the Large and Small Grid


def plot_accuracy(raw_all_grids_df, option=None):
    """
    Input:  raw condition df
            facets: None, 'subjects', 
    Output: figure(s) that visualize the difference in accuracy btw. el and pl
    """

    # Rearrange columns for better readability in temporal order of the experiment          
    condition_list = raw_all_grids_df['condition'].value_counts().index.tolist()
    condition_list_sorted = ['GRID', 'SMALLGRID_BEFORE', 'SMALLGRID_AFTER']
    if not set(condition_list).issubset(set(condition_list_sorted)) :
        raise ValueError('are you sure everything is okay with the condition reordering?')
        
    # Create a categorical type
    condition_cat = CategoricalDtype(categories=condition_list_sorted, ordered=True)
    # Cast the existing categories into the new category. Due to a bug in pandas we need to do this via a string.
    raw_all_grids_df['condition'] = raw_all_grids_df['condition'].astype(str).astype(condition_cat)


    # Get the x and y position of the 13 elements shown in the small Grid condition
    element_pairs = raw_all_grids_df.query('condition=="SMALLGRID_BEFORE"').loc[:,['posx', 'posy']]
    only_13_elements = pd.merge(raw_all_grids_df, element_pairs, on=['posx', 'posy'], how='inner')
   
    # get data grouped
    mean_for_each_subject_and_condition = helper.group_to_level_and_take_mean(only_13_elements, lowestlevel='condition')

    if option is None:
        # compare accuracy values btw eyetrackers. Taking the mean over the subjects
        (ggplot(mean_for_each_subject_and_condition, aes(x='et', y='accuracy',color='condition')) +
                # TODO or points or violins??
                geom_boxplot(data=mean_for_each_subject_and_condition, position=position_dodge(width=0.9)) +
                ggtitle('Comparing accuracy of conditions')).draw()
 
    
    elif option == 'facet_subjects':
        # plot mean accuracy over all blocks for each subject
        (ggplot(mean_for_each_subject_and_condition, aes(x='et', y='accuracy',color='condition')) +
                geom_point(alpha=0.1,data=mean_for_each_subject_and_condition, position=position_dodge(width=0.5)) +
                geom_point(position=position_dodge(width=0.5)) +
                geom_line(aes(group='condition'),alpha=0.6, position=position_dodge(width=0.5)) +
                facet_grid('.~subject') + 
                ggtitle('Comparing accuracy of conditions')).draw()


    elif option == 'show_variance_for_blocks':
        # plot mean accuracy over all blocks for each subject and show range by plotting the mean accuracy for each block
        (ggplot(mean_for_each_subject_and_condition, aes(x='et', y='accuracy',color='condition')) +
        # get the mean for each block
        geom_point(alpha=0.1,data=raw_all_grids_df.groupby(['et', 'subject','condition','block']).mean().reset_index(level=['et','subject','condition','block']),position=position_dodge(width=0.5)) +
        geom_point(position=position_dodge(width=0.5))+
        geom_line(aes(group='condition'),position=position_dodge(width=0.5)) +
        facet_grid('.~subject') + 
        ggtitle('Comparing accuracy of conditions')).draw()


    elif option == 'final_figure':
        # plot that we wanted: See "Schmierzettel"
        # TODO I still need to do this
        # tanking the mean
       
        # look up which range linerange takes
        
        # simple: eyetracker vs  mean accuracy over all blocks and subjects
        (ggplot(mean_for_each_subject_and_condition) +
                  stat_summary(aes(x='condition', y='accuracy', fill='et'), fun_y=np.mean, geom='point')+
                  stat_summary(aes(x='condition', y='accuracy', fill='et'), geom='linerange') +
                  ggtitle('Accuracy in different grid condition based on 13 elements')).draw()
                

    else:
        raise ValueError('You must set facets to a valid option. See documentation.')






def display_fixations(raw_all_grids_df, option='fixations'):
    """
    Displaying accuracy on grid points
    
    options are: 'fixations'
    """
    # I think I make a mistake here
    #TODO check why I thought I have to do this?
    # I would rather plot from the raw_large_grid_df directly ??
    # group data so that we have one fixation observation for each grid point in each block and for each subject and for each eyetracker
    grouped_elem_pos = raw_all_grids_df.groupby(['et', 'subject','posx', 'posy', 'condition']).mean().reset_index(level=['et', 'subject','posx', 'posy', 'condition']).drop(columns = ['end_time','start_time','msg_time'])

    
    # make separate figure for each eyetracker
    for eyetracker in [['EyeLink'], ['Pupil Labs']]:
        et_grouped_elem_pos = grouped_elem_pos.query('et==@eyetracker')    
        
        if option == 'fixations':
            # visualize fixations and make facets: subjects vs conditions
            (ggplot(aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)'), data= et_grouped_elem_pos) +
            geom_point(show_legend=False) + 
            guides(color=guide_legend(ncol=40)) +
            facet_grid('condition~subject')+
            ggtitle(str(eyetracker)[2:-2] + ': Different Grid conditions')).draw()

        else:
            raise ValueError('You must set option to a valid string. See documentation.')











