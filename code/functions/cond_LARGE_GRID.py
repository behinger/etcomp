#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 16:57:07 2018

@author:  kgross
"""

import functions.add_path
import pandas as pd
import numpy as np
import os

import functions.et_preprocess as preprocess


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#%%


# specify subject
subject = 'VP4'

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)

# which et do you want to examine?
etsamples = plsamples
etmsgs = plmsgs
etevents = plevents
# or
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents


#%% LETS try for one subject first

# get the last fixation for element 1 in block 1 LARGE GRID

Large_Grid = pd.DataFrame()



#%% Sanity checks

# there should not be any NaN values
if Large_Grid.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')
    
    
    

#%% Make a for loop over the foldernames (subjectnames)   and have a list of subjects that we exclude from analysis
#Also loop over the et

    
    
subjectnames = get them from folder
rejected_subjects = ['VP5']

ets = ['pl', 'el']    


for subject in (subjectnames - rejected_subjects):
    for et in ets:
        
        