# -*- coding: utf-8 -*-

import functions.add_path

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_make_df as make_df
import functions.et_helper as  helper
import functions.et_plotting as etplot
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.et_preprocess as preprocess
import functions.pl_detect_blinks as pl_blinks
from functions.detect_events import make_blinks,make_saccades,make_fixations



#%% LOAD DATA and preprocess RAW data for ALL subjects

# to initialize logging
import functions.init_logger
import logging


# loop over the foldernames (subjectnames)
# restricted to subjects that we do not exclude from analysis
# also loop over the et
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
#TODO find out whats wrong with vp3 and vp12 and fix and then use vp3 again!!
rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP21', 'VP7', 'VP3', 'VP12']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['el', 'pl']    


# get a logger
logger = logging.getLogger(__name__)



#%% preprocess for all subjects
for subject in subjectnames:
    for et in ets:
        logger.critical(' ')
        logger.critical('Eyetracker: %s    Subject: %s ', et, subject)
        etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))


#%% CALCULATE data and preprocess RAW data for ONE subject

# specify subject
subject = 'VP7'

# preprocess pl data
plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))

# preprocess el data
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))



#%% LOAD preprocessed data from csv file

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)



# which et do you want to examine?
et_str = 'pl'
etsamples = plsamples
etmsgs = plmsgs
etevents = plevents
# or
et_str = 'el'
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents


# have a look at time and gx
plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')



#%% Figure to examine which samples we exclude

# get uncleaned data samples
datapath='/net/store/nbp/projects/etcomp/'
preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
etsamples = pd.read_csv(os.path.join(preprocessed_path,str(et_str+'_samples.csv')))


plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')

plt.plot(etsamples.query('type=="blink"')['smpl_time'],etsamples.query('type=="blink"')['gx'],'o')
plt.plot(etsamples.query('type=="saccade"')['smpl_time'],etsamples.query('type=="saccade"')['gx'],'o')
plt.plot(etsamples.query('type=="fixation"')['smpl_time'],etsamples.query('type=="fixation"')['gx'],'o')
plt.legend(['sample','blink','saccade','fixation'])

plt.title(str(et_str + " " + subject))

# if you want to look at the not cleaned data, you should set the yaxis
plt.ylim([-50,2500])


plt.plot(etsamples.query('neg_time==True')['smpl_time'],etsamples.query('neg_time==True')['gx'],'o')
plt.plot(etsamples.query('outside==True')['smpl_time'],etsamples.query('outside==True')['gx'],'o')
plt.plot(etsamples.query('zero_pa==True')['smpl_time'],etsamples.query('zero_pa==True')['gx'],'o')



#%% Call plots from analysis here


# change into code folder
os.chdir('/net/store/nbp/users/kgross/etcomp/code')

import LARGE_GRID 
import LARGE_and_SMALL_GRID
import FREEVIEW

import functions.et_condition_df as condition_df

subjectnames      = ['VP3', 'VP4', 'VP1']


# LARGE GRID

# load grid df for subjectnames
raw_large_grid_df = condition_df.get_condition_df(subjectnames, ets, condition='LARGE_GRID')

# plot accuracy    
LARGE_GRID.plot_accuracy(raw_large_grid_df, facets=None)
LARGE_GRID.plot_accuracy(raw_large_grid_df, facets='subjects')
LARGE_GRID.plot_accuracy(raw_large_grid_df, facets='dodge')

# plot accuracy components
LARGE_GRID.compare_accuracy_components(raw_large_grid_df)
LARGE_GRID.compare_accuracy_components(raw_large_grid_df, display_precision=True)

# look at numerical accuracies in table
table_large_grid_accuracy = LARGE_GRID.make_table_accuracy(raw_large_grid_df)
print(table_large_grid_accuracy.to_string())

# investigate on the position and properties
LARGE_GRID.display_fixations(raw_large_grid_df, option='fixations')
LARGE_GRID.display_fixations(raw_large_grid_df, option='accuracy_for_each_element')
LARGE_GRID.display_fixations(raw_large_grid_df, option='precision_for_each_element')
LARGE_GRID.display_fixations(raw_large_grid_df, option='offset')



# LARGE and SMALL GRID
raw_large_and_small_grid_df = condition_df.get_condition_df(subjectnames, ets, condition='LARGE_and_SMALL_GRID')
LARGE_and_SMALL_GRID.plot_accuracy(raw_large_and_small_grid_df, facets=None)


# Freeviewing
FREEVIEW.plot_histogram(subjectnames)
FREEVIEW.plot_heatmap(subjectnames)










