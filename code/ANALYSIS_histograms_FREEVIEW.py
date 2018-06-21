#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 17:30:38 2018

@author: kgross
"""

import functions.add_path
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *



import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.ANALYSIS_get_condition_df as get_condition_df

import logging


theme_set( theme_minimal(base_size=12) + theme(text = element_text(),\
               panel_background = element_rect(colour = 'None'),\
               plot_background = element_rect(colour = 'None'),\
               panel_border = element_rect(colour = 'None'),\
               axis_title = element_text(size = 10),\
               axis_title_y = element_text(angle=90,vjust =2),\
               axis_title_x = element_text(vjust = -0.2),\
               axis_text = element_text(),\
               axis_line = element_line(colour="black"),\
               axis_ticks = element_line(),\
               panel_grid_major = element_line(colour="#f0f0f0"),\
               panel_grid_minor = element_blank(),\
               legend_key = element_rect(colour = 'None'),\
               legend_position = "bottom",\
               legend_background=element_rect(fill='None',color='None'),\
               legend_direction = "horizontal",\
               legend_box = 'horizontal',\
               legend_margin = 0,\
               legend_title = element_text(size=10),\
               strip_background=element_rect(colour="#ffffff",fill="#ffffff"),\
               strip_text = element_text(face="bold")))
               
               
#%% get FREEVIEW df


# specify which subjects you want to analyze
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', '007', 'log_files', 'surface', 'VP3', 'VP7', 'VP8', 'VP12', 'VP15']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    


# load freeview df for all subjects
complete_freeview_df, complete_fix_count_df = get_condition_df.get_complete_freeview_df(subjectnames, ets)


# Sanity check
# there should not be any NaN values
if complete_freeview_df.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')
    


               
#%% main sequence
    
!!!!!!!!SACCADES!!!!!!!!!!!!!
