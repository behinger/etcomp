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

import matplotlib.pyplot as pltE
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
               axis_title_y = element_text(angle=90,vjust =0),\
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
               legend_margin = 10,\
               legend_title = element_text(size=10),\
               legend_title_align = 'left',\
               strip_background=element_rect(colour="#ffffff",fill="#ffffff"),\
               strip_text = element_text(face="bold")))
               
               
#%% get FREEVIEW df


# specify which subjects you want to analyze
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', '007', 'log_files', 'surface', 'VP3','VP1', 'VP7', 'VP8', 'VP12', 'VP15']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    


# load freeview df for all subjects
complete_freeview_df, complete_fix_count_df = get_condition_df.get_complete_freeview_df(subjectnames, ets)


# Sanity check
# there should not be any NaN values
if complete_freeview_df.isnull().values.any():
    raise ValueError('Some value(s) of the df is NaN')
    
    
#%% Make variables categorical
    
complete_fix_count_df.dtypes
# TODO : rename el into EyeLink
complete_fix_count_df[complete_fix_count_df.select_dtypes(['object']).columns] = complete_fix_count_df.select_dtypes(['object']).apply(lambda x: x.astype('category'))
complete_freeview_df[complete_freeview_df.select_dtypes(['object']).columns] = complete_freeview_df.select_dtypes(['object']).apply(lambda x: x.astype('category'))




complete_fix_count_df["et"] = complete_fix_count_df["et"].astype('category')
complete_fix_count_df["subject"] = complete_fix_count_df["subject"].astype('category')
complete_fix_count_df["block"] = complete_fix_count_df["block"].astype('category')

complete_fix_count_df["trial"] = complete_fix_count_df["trial"].astype('category')
complete_fix_count_df["pic_id"] = complete_fix_count_df["pic_id"].astype('category')

    
#%% Look at pi_ids


np.sort(complete_fix_count_df.pic_id.unique())

np.sort(complete_fix_count_df.query("subject == 'VP1'").pic_id.unique())

# TODO pic_id 5 and 6 are missing
np.sort(complete_fix_count_df.query("subject == 'VP2' & et == 'pl'").pic_id.unique())



    
#%% Plot for multiple subjects and both eye trackes
  
# investigate on the number of fixations

# shows number of fixations per picture for each eye tracker (facets over subjects)   
ggplot(complete_fix_count_df, aes(x='et', y='fix_counts', color = 'factor(pic_id)')) \
        + geom_point(alpha=0.4) \
        + geom_line(aes(group='pic_id')) \
        + guides(color=guide_legend(ncol=40)) \
        + facet_grid('.~subject') \
        + xlab('Eyetracker') \
        + ylab('Number of fixations') \
        + ggtitle('EyeLink vs PupilLabs: Number of fixations for each picture') 
      



# using boxplot to compare eye tracker overall
ggplot(complete_fix_count_df, aes(x='et', y='fix_counts')) \
        + geom_boxplot(aes(fill='et'), color='k', alpha=0.2, outlier_color='r', outlier_size=1.5, show_legend=False) \
        + ylab('Number of fixations per picture') \
        + ggtitle('EyeLink vs PupilLabs: Mean number of fixations for each picture')


# using violin to compare eye tracker overall
# TODO sth woring here 
ggplot(complete_fix_count_df, aes(x='et', y='fix_counts')) \
        + geom_violin(aes(color='et', fill='et'), alpha = 0.25, show_legend=False) \
        + xlab('Eyetracker') \
        + ylab('Number of fixations') \
        + ggtitle('EyeLink vs PupilLabs: Mean number of fixations')




   
#%% investigate on the position of fixations (use density)

# TODO maybe do this first
# select only important columns       
freeview_df = complete_freeview_df.drop(columns=['msg_time', 'condition', 'exp_event', 'type', 'euc_fix_rms'])
freeview_df["pic_id"] = freeview_df["pic_id"].astype('category')

freeview_df.dtypes


# only for sanity:
# plotting all fixations for each eye tracker
ggplot(complete_freeview_df, aes(x='mean_gx', y='mean_gy')) \
        + geom_point(aes(size = 'duration', color = 'pic_id')) \
        + guides(color=guide_legend(ncol=40)) \
        + facet_grid('.~et') \
        + ggtitle('EyeLink vs PupilLabs: All fixations of all subjects of all trials')



# looking at density distributions
# for each gaze component (horizontal/vertical) and for each eyetracker
gaze_comp_freeview_df = freeview_df.melt(id_vars=['et', 'subject', 'block', 'trial', 'pic_id', 'start_time', 'end_time', 'duration', 'spher_fix_rms'], var_name='gaze_comp')

# display both eye tracker in the same plot
ggplot(gaze_comp_freeview_df, aes(x='value', color = 'et')) \
       + stat_density(geom='line', kernel='gaussian') \
       + xlab('Position in visual angle (degrees)') \
       + facet_grid('.~gaze_comp')


#TODO: DISCUSS what i am seeing and the meaning of the hoehenlinien
# using a 2D visualization for the density
ggplot(freeview_df, aes(x='mean_gx', y='mean_gy')) \
    + stat_density_2d() \
    + facet_grid('.~et') \
    + ggtitle('EyeLink vs PupilLabs: Density distribution over all subjects and all trials')







# JUST FOR ME
ggplot(freeview_df, aes(x='mean_gx', y='mean_gy')) \
    + geom_point(alpha = 0.25, color='red') \
    + stat_density_2d() \
    + facet_grid('.~et') \
    + ggtitle('EyeLink vs PupilLabs: Density distribution over all subjects and all trials')







   
#%% Make a heatmap
 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage.filters import gaussian_filter


# picture size

def px2deg(px, pxPerDeg=0.276,distance=600):
          
    deg = 2*np.arctan2(px*pxPerDeg,distance)*180/np.pi

    return deg


# the picture has a size of 1200 x 1500 pixels
# the pictures is centered  --> therefore divide by 2
pic_horizontal = px2deg(1500*0.6) / 2
pic_vertical = px2deg(1200*0.6) / 2





# make 5000 bins from - picturesize in degrees to picturesize in degrees with a stepsize of 0.01
def myplot(x, y, s, bins=[np.arange(-pic_horizontal,pic_horizontal,step=0.01),np.arange(-pic_vertical,pic_vertical,step=0.01)]):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap.T, extent




fig, axs = plt.subplots(2, 2)

# mean fixation location data
x_pl = list(freeview_df.query('et == "pl"').mean_gx)
y_pl = list(freeview_df.query('et == "pl"').mean_gy)


x_el = list(freeview_df.query('et == "el"').mean_gx)
y_el = list(freeview_df.query('et == "el"').mean_gy)


sigmas = [0, 300, 0, 300]

axs[0,0].plot(x_pl, y_pl, 'k.', markersize=5)
axs[0,0].set_title("PL Scatter plot")

img, extent = myplot(x_pl,y_pl, sigmas[1])
axs[0,1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
axs[0,1].set_title("PL Smoothing with  $\sigma$ = %d" % sigmas[1])

axs[1,0].plot(x_el, y_el, 'k.', markersize=5)
axs[1,0].set_title("EL Scatter plot")

img, extent = myplot(x_el, y_el, sigmas[3])
axs[1,1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
axs[1,1].set_title("EL Smoothing with  $\sigma$ = %d" % sigmas[3])

plt.show()




















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

