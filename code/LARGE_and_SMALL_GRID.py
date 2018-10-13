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
import functions.plotnine_theme as mythemes

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.et_make_df as  make_df
import functions.et_condition_df as condition_df
from functions.detect_events import make_blinks,make_saccades,make_fixations

from functions.et_helper import winmean,winmean_cl_boot

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
   
  
    # specify aggregators for different levels    
    #  element level   - -   block level   - -    (subject level)
    #       mean               median                  (mean)
    
    agg_level=[winmean, winmean]
    
    # aggregate data of only_13_elements
    mean_over_elements                    = only_13_elements.groupby(['condition', 'block','subject','et'], as_index=False).agg(agg_level[0])
    winmean_over_elements_winmean_over_blocks = mean_over_elements.groupby(['condition', 'subject','et'], as_index=False).agg(agg_level[1])

    
    if option is None:
        # compare accuracy values btw eyetrackers. Taking the mean over the subjects
        (ggplot(winmean_over_elements_winmean_over_blocks, aes(x='et', y='accuracy',color='condition')) +
                # TODO or points or violins??
                geom_boxplot(data=winmean_over_elements_winmean_over_blocks, position=position_dodge(width=0.9)) +
                ggtitle('Comparing accuracy of conditions')).draw()
 
    
    elif option == 'facet_subjects':
        # plot mean accuracy over all blocks for each subject
        (ggplot(winmean_over_elements_winmean_over_blocks, aes(x='et', y='accuracy',color='condition')) +
                geom_point(alpha=0.1,data=winmean_over_elements_winmean_over_blocks, position=position_dodge(width=0.5)) +
                geom_point(position=position_dodge(width=0.5)) +
                geom_line(aes(group='condition'),alpha=0.6, position=position_dodge(width=0.5)) +
                facet_grid('.~subject') + 
                ggtitle('Comparing accuracy of conditions')).draw()


    elif option == 'show_variance_for_blocks':
        # plot mean accuracy over all blocks for each subject and show range by plotting the mean accuracy for each block
        (ggplot(winmean_over_elements_winmean_over_blocks, aes(x='et', y='accuracy',color='condition')) +
        # get the mean for each block
        geom_point(alpha=0.1,data=raw_all_grids_df.groupby(['et', 'subject','condition','block']).mean().reset_index(level=['et','subject','condition','block']),position=position_dodge(width=0.5)) +
        geom_point(position=position_dodge(width=0.5))+
        geom_line(aes(group='condition'),position=position_dodge(width=0.5)) +
        facet_grid('.~subject') + 
        ggtitle('Comparing accuracy of conditions')).draw()


    elif option == 'final_figure':     
        
        # save old theme and set the one for fixation plotting
        old_theme = theme_get()
        theme_set(mythemes.before_after_grid_theme)

            
        # simple: eyetracker vs  mean accuracy over all blocks and subjects
        return (ggplot(winmean_over_elements_winmean_over_blocks,aes(x='condition', y='accuracy', fill='et',group='et', color='et')) +
                      stat_summary(fun_y=winmean, geom='line',position=position_dodge(width=0.1)) +
                      # pointrange makes a 0.95 bootstrap CI
                      stat_summary(fun_data=winmean_cl_boot, geom='pointrange', position=position_dodge(width=0.1)) +
                      #geom_point(aes(group="subject"),data=winmean_over_elements_winmean_over_blocks.query("et=='Pupil Labs'"),alpha=0.5,color='blue')+
                      #geom_point(aes(group="subject"),data=winmean_over_elements_winmean_over_blocks.query("et=='EyeLink'"),alpha=0.5,color='red')+
                      ylab("Accuracy [$^\circ$]") +
                      labs(title='Course of Accuracy'))                
    
        # restore old theme
        theme_set(old_theme)
    
    elif option == 'subjectvariance':
        mean_over_elements.loc[:,'group'] = mean_over_elements.et + mean_over_elements.block
        return (ggplot(mean_over_elements,aes(x='condition', y='accuracy', fill='et',group='group', color='et')) +
                    geom_point(alpha=0.5)+
                    geom_line()+
                      ylab("Accuracy [$^\circ$]") +
                      labs(title='Course of Accuracy'))+facet_wrap('subject',scales='free')  
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











