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
# specify costumed minimal theme
import functions.plotnine_theme



import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.ANALYSIS_get_condition_df as get_condition_df

import logging
               
               
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
