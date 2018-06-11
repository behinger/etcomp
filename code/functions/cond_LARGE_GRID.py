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
all_large_grid_fix = merged_events.query('condition == "GRID"').loc[:,['type', 'end_time', 'mean_gx','duration', 'start_time', 'fix_rms', 'mean_gy', 'block', 'condition', 'element', 'exp_event', 'grid_size', 'msg_time', 'posx', 'posy']]

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
           geom_point(aes(size='fix_rms', color='factor(mean_gx * mean_gy)'))+\
           geom_point(aes(x='posx_elem', y='posy_elem', color='factor(posx_elem * posy_elem)'),data = grid_elements)+\
           facet_wrap('~block')+\
           ggtitle(et_str + ': Large Grid using only last fixation: size : rms')
 

gridplot

#%% Sanity checks

# there should not be any NaN values
if large_grid_df.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')
    
        


       