#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 19:47:14 2018

@author: kgross
"""


import functions.add_path
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *
#from plotnine.stat_density_2d import stat_density_2d
#from plotnine import ggplot, aes, geom_point, stat_hull, theme



import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.make_df as  make_df
from functions.detect_events import make_blinks,make_saccades,make_fixations



import logging


#%% get FREEVIEW df


# get the complete large grid df

foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', '007', 'log_files', 'surface', 'VP3', 'VP7', 'VP8', 'VP12', 'VP15']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    


complete_freeview_df, complete_fix_count_df = get_complete_freeview_df(subjectnames, ets)





#%% Sanity checks

# there should not be any NaN values
if complete_freeview_df.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')
    
    
#%% Plot for multiple subjects and both eye trackes
    
    
# investigate on the number of fixations

# compare eye tracker for each subject   
ggplot(complete_fix_count_df, aes(x='factor(et).codes', y='fix_counts', color = 'factor(pic_id)')) \
        + geom_point(alpha=0.4) \
        + geom_line(aes(group='pic_id')) \
        + facet_grid('.~subject')


# using boxplot to compare eye tracker overall
ggplot(complete_fix_count_df, aes(x='et', y='fix_counts')) \
        + geom_boxplot() \
        + ggtitle('Mean number of fixations for each picture')




# investigate on the position of fixations (use density)
freeview_df = complete_freeview_df.drop(columns=['msg_time', 'condition', 'exp_event', 'type', 'euc_fix_rms'])

# plotting all fixations for each eye tracker
ggplot(freeview_df, aes(x='mean_gx', y='mean_gy')) \
        + geom_point(aes(size = 'duration', color = 'factor(pic_id)')) \
        + facet_grid('.~et')


# looking at density distributions for each gaze component (horizontal/vertical) and for each eyetracker
gaze_comp_freeview_df = freeview_df.melt(id_vars=['et', 'subject', 'block', 'trial', 'pic_id', 'start_time', 'end_time', 'duration', 'spher_fix_rms'], var_name='gaze_comp')

# display both eye tracker in the same plot
ggplot(gaze_comp_freeview_df, aes(x='value', color = 'et')) \
       + geom_density(kernel='gaussian', alpha=.3, trim=True) \
       + facet_grid('.~gaze_comp')









































#%% Freeviewing
# LETS try for one subject first

# load preprocessed data for one subject
subject = 'VP1'

elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)

et_str = 'el'
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents

# forward merge to add msgs to the events
merged_events = helper.add_msg_to_event(etevents, etmsgs.query('condition=="FREEVIEW"'), timefield = 'start_time', direction='forward')

# get all relevant columns
all_freeview_events = merged_events.loc[:,['msg_time',  'condition', 'exp_event','block', 'trial', 'pic_id', 'type','start_time', 'end_time','duration', 'mean_gx', 'mean_gy', 'euc_fix_rms', 'spher_fix_rms']]


# select only fixations while picture was presented
freeview_fixations = all_freeview_events.query("type == 'fixation' & exp_event == 'trial'")

# count how many fixations per trail   in seperate dataframe  (use as sanity check)
fix_count = freeview_fixations.groupby(['block', 'trial']).size().reset_index(name='fix_counts')



# block 1 trial 1

block_trial_1 = freeview_fixations.query("block == 1 & trial == 1")



ggplot(block_trial_1, aes(x='mean_gx', y='mean_gy')) \
        + geom_point(aes(size = 'duration', color = 'pic_id'))




# density for mean gx and gy over all pictures
ggplot(freeview_fixations, aes(x='mean_gx')) + geom_density()
# ggplot(freeview_fixations, aes(x = 'mean_gx')) + stat_density()
ggplot(freeview_fixations, aes(x='mean_gy')) + geom_density()



ggplot(freeview_fixations, aes(x='mean_gx')) \
       + geom_density(kernel='gaussian', alpha=.3, trim=True)


p = (ggplot(mtcars)
     + aes('wt', 'mpg', color='factor(cyl)')
     + geom_point()
     + stat_hull(size=1)
     )



# stat density 2d

ggplot(freeview_fixations, aes(x='mean_gx', y='mean_gy')) + stat_density_2d()

ggplot(freeview_fixations, aes(x='mean_gx', y='mean_gy')) \
  + geom_point() \
  + stat_density_2d()
  
ggplot(wdata, aes(x = weight)) + stat_density()

