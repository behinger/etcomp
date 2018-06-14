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

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.make_df as  make_df
from functions.detect_events import make_blinks,make_saccades,make_fixations

import logging

#%% LETS try for one subject first

# load preprocessed data for one subject

# TODO we loose element 1 when merging
merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time')

# all fixations made during GRID condition 
# !not relevant later on!
all_large_grid_fix = merged_events.query('condition == "GRID"').loc[:,['type', 'end_time', 'mean_gx','duration', 'start_time', 'euc_fix_rms', 'mean_gy', 'block', 'condition', 'element', 'exp_event', 'grid_size', 'msg_time', 'posx', 'posy']]

# make df for grid condition that only contains ONE fixation per element
# (the last fixation before the new element  (used a groupby.last() to achieve that))
large_grid_df = make_df.make_large_grid_df(merged_events)



#%% Get df of displayed elements

# make a df that contains all grid element positions
# all displayed Large Grids are the same
grid_elements = pd.DataFrame(data=[large_grid_df.groupby('element').first()['posx'].values, large_grid_df.groupby('element').first()['posy'].values]).T
grid_elements.columns = ['posx_elem', 'posy_elem']
 
#%% SAVE the plot in repository
 
plotname = 'GRID_' + et_str + '_' + subject

gridplot.save(filename=plotname, format=None, path='/net/store/nbp/users/kgross/etcomp/plots', dpi=600, verbose=True)




#%% PLOTS

# plots always use fixations as main df and then at the end a layer of the shown GRID elements is added


# all fixations
gridplot = ggplot(all_large_grid_fix, aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)')) +\
           geom_point()+\
           geom_point(aes(x='posx_elem', y='posy_elem', color='factor(posx_elem * posy_elem)'),data = grid_elements)+\
           facet_wrap('~block')+\
           ggtitle(et_str + ': Large Grid using all fixations')+\
           scale_color_discrete(guide=False)
           

# simple
gridplot = ggplot(large_grid_df, aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)')) +\
           geom_point()+\
           geom_point(aes(x='posx_elem', y='posy_elem', color='factor(posx_elem * posy_elem)'), data = grid_elements)+\
           facet_wrap('~block')+\
           ggtitle(et_str + ': Large Grid using only last fixation')
  

# with rms
gridplot = ggplot(large_grid_df, aes(x='mean_gx', y='mean_gy')) +\
           geom_point(aes(size='euc_fix_rms', color='factor(mean_gx * mean_gy)'))+\
           geom_point(aes(x='posx_elem', y='posy_elem', color='factor(posx_elem * posy_elem)'),data = grid_elements)+\
           facet_wrap('~block')+\
           ggtitle(et_str + ': Large Grid using only last fixation: size : rms_euc')
 

gridplot



#%%
#%% 

#%% Create large_grid_df for all subjects

foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    



#%% Get df of displayed elements


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
            merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time')
                       
            # make df for grid condition that only contains ONE fixation per element
            # (the last fixation before the new element  (used a groupby.last() to achieve that))
            large_grid_df = make_df.make_large_grid_df(merged_events)          
            
            # add a column for eyetracker and subject
            large_grid_df['et'] = et
            large_grid_df['subject'] = subject
            
            # concatenate to the complete df
            complete_large_grid_df = pd.concat([complete_large_grid_df,large_grid_df])
                   
    return complete_large_grid_df


complete_large_grid_df = get_complete_large_grid_df(subjectnames, ets)

#%% Sanity checks

# there should not be any NaN values
if complete_large_grid_df.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')
    
     
#%% Making plots for all subjects
   

# get df grouped by et and subject 
# take the mean of the accuracy and precision measures
grouped_large_grid_df = complete_large_grid_df.groupby(['et', 'subject']).mean().loc[:,['fix_rms', 'spher_accuracy', 'hori_accuracy', 'vert_accuracy', 'euc_accuracy']]
grouped_large_grid_df.reset_index(level=['et', 'subject'], inplace=True)



# simple
ggplot(grouped_large_grid_df, aes(x='factor(et).codes', y='spher_accuracy', color='subject')) +\
          geom_line() +\
          geom_point() +\
          ggtitle('Spherical accuracy in visual degrees')


# subject facets
ggplot(grouped_large_grid_df, aes(x='factor(et).codes', y='spher_accuracy', color='subject')) +\
          geom_line() +\
          geom_point() +\
          facet_grid('.~subject')+\
          ggtitle('Spherical accuracy in visual degrees')


# using stat_summary
ggplot(aes(x='factor(et).codes', y='spher_accuracy',color='factor(block)'), data=complete_large_grid_df.groupby(['et', 'subject','block']).mean().reset_index(level=['et','subject','block'])) +\
        geom_point(alpha=0.1,data=complete_large_grid_df,position=position_dodge(width=0.7)) +\
        geom_point(position=position_dodge(width=0.7))+geom_line(aes(group='block'),position=position_dodge(width=0.7)) +\
        facet_grid('.~subject') + \
        ggtitle('Using stat summary')
#        stat_summary(color='red') +\

ggplot(aes(x='et', y='spher_accuracy'), data=grouped_large_grid_df) +\
        geom_boxplot() +\
        ggtitle('Using boxplot')







ggplot(grouped_large_grid_df, aes(x='et', y='euc_accuracy', color='subject')) +\
           geom_point() +\
           facet_wrap('~subject')+\
           ggtitle('Trying')


ggplot(grouped_large_grid_df, aes(x='et', y='fix_rms', color='subject')) +\
          geom_point() +\
          facet_wrap('~subject')+\
          ggtitle('Trying')




gridplot


   
#%% different MEASURES
   
# use melt to investigate on different measures

melted_measures = grouped_large_grid_df.melt(id_vars=['et', 'subject'], var_name='measure')

ggplot(melted_measures, aes(x='factor(et).codes', y='value', color='subject')) +\
          geom_line() +\
          geom_point() +\
          facet_grid('measure~subject')+\
          ggtitle('Investigating on measures')

ggplot(melted_measures, aes(x='factor(et).codes', y='value', color='measure')) +\
          geom_line() +\
          geom_point() +\
          facet_grid('.~subject')+\
          ggtitle('Investigating on measures')




   
#%% Displaying accuracy on grid points


grid_elements = pd.DataFrame(data=[large_grid_df.groupby('element').first()['posx'].values, large_grid_df.groupby('element').first()['posy'].values]).T
grid_elements.columns = ['posx_elem', 'posy_elem']
 
ggplot(complete_large_grid_df, aes(x='factor(et).codes', y='spher_accuracy', color='subject')) +\
          geom_line() +\
          geom_point() +\
          ggtitle('Grid')



grouped_elem_pos = complete_large_grid_df.groupby(['et', 'subject','posx', 'posy', 'block']).mean().reset_index(level=['et', 'subject','posx', 'posy', 'block']).drop(columns = ['end_time','start_time','msg_time'])


el_grouped_elem_pos = grouped_elem_pos.query('et == "el"')

pl_grouped_elem_pos = grouped_elem_pos.query('et == "pl"')

#compare blocks and subjects
ggplot(aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)'), data= el_grouped_elem_pos) +\
        geom_point() + \
        facet_grid('block~subject')+\
        ggtitle('Grid Eyelink')


# rms
ggplot(aes(x='mean_gx', y='mean_gy', size='fix_rms'), data=pl_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +\
        geom_point() +\
        facet_wrap('~subject')+\
        ggtitle('RMS Grid Pupillabs')

# sphere_accuracy
ggplot(aes(x='mean_gx', y='mean_gy', size='spher_accuracy'), data=pl_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +\
        geom_point() +\
        facet_wrap('~subject')+\
        ggtitle('ACC Grid Pupillabs')






