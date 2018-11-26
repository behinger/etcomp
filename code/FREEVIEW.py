#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 19:47:14 2018

@author: kgross
"""


import functions.add_path

import functions.et_preprocess as preprocess

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from scipy.ndimage.filters import gaussian_filter
from scipy.misc import imread

from plotnine import *
# specify costumed minimal theme
import functions.plotnine_theme as mythemes

import functions.et_helper as  helper
from functions.et_helper import winmean,winmean_cl_boot

import logging
import os




def plot_heatmap(raw_freeview_df,raw_fix_count_df, only_horizontal_heatmap=True):
    """
    Make a heatmap of the freeview fixation df
    """
    
    # the pictures have a size of 1200 x 1500 pixels
    # factor of 0.6 as we scaled the  pictures in the matlabscript (experiment)
    # they are centered  --> divide by 2
    pic_size_horizontal = helper.size_px2deg(1500*0.6) 
    pic_size_vertical = helper.size_px2deg(1200*0.6) 
    
    
    # mean fixation location data
    pl_x_coords = list(raw_freeview_df.query('et == "Pupil Labs"').mean_gx)
    pl_y_coords = list(raw_freeview_df.query('et == "Pupil Labs"').mean_gy)
    
    el_x_coords = list(raw_freeview_df.query('et == "EyeLink"').mean_gx)
    el_y_coords = list(raw_freeview_df.query('et == "EyeLink"').mean_gy)
    
    # there must be the same number of x and y gaze fixation positions
    assert(len(pl_x_coords) == len(pl_y_coords))
    assert(len(el_x_coords) == len(el_y_coords))


    # these are the sigmas for the Kernel
    # 0 : no smoothing for the scatterplot
    # 300: we selected 300 std as we want 3 degrees visual angle and have bins of size 0.01
    sigmas = [0, 300, 0, 300]

    if only_horizontal_heatmap:
        # make a figure that has 2 subplots (aligned horizontally)
        fig, axs = plt.subplots(1, 2)
        
        # Pupil Labs heatmap
        img, extent = make_heatmap(pl_x_coords,pl_y_coords, sigmas[1], pic_size_horizontal, pic_size_vertical)
        axs[0].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[0].set_aspect('equal')
        axs[0].set_title("Pupil Labs Smoothing with 3 $^\circ$")

        # EyeLink heatmap    
        img, extent = make_heatmap(el_x_coords, el_y_coords, sigmas[3], pic_size_horizontal, pic_size_vertical)
        axs[1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[1].set_aspect('equal')
        axs[1].set_title("EyeLink Smoothing with 3 $^\circ$")
        
        plt.show()
        
        
    else:
        # make a figure that has 4 subplots
        fig, axs = plt.subplots(2, 2)


        # Pupil Labs heatmap
        img, extent = make_heatmap(pl_x_coords,pl_y_coords, sigmas[1], pic_size_horizontal, pic_size_vertical)
        axs[0,1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[0,1].set_aspect('equal')
        axs[0,1].set_title("Pupil Labs Smoothing with 3 $^\circ$")

        # Pupil Labs scatterplot
        axs[0,0].plot(pl_x_coords, pl_y_coords, 'k.', markersize=5)
        axs[0,0].set_aspect('equal')  
        axs[0, 0].set_xlim(extent[0], extent[1])
        axs[0, 0].set_ylim(extent[2], extent[3])
        axs[0,0].set_title("Pupil Labs Scatter plot")


        # EyeLink heatmap    
        img, extent = make_heatmap(el_x_coords, el_y_coords, sigmas[3], pic_size_horizontal, pic_size_vertical)
        axs[1,1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[1,1].set_aspect('equal')
        axs[1,1].set_title("EyeLink Smoothing with 3 $^\circ$")

        # EyeLink scatterplot
        axs[1,0].plot(el_x_coords, el_y_coords, 'k.', markersize=5)
        axs[1,0].set_aspect('equal')
        axs[1, 0].set_xlim(extent[0], extent[1])
        axs[1, 0].set_ylim(extent[2], extent[3])
        axs[1,0].set_title("EyeLink Scatter plot")


        # put info into generated files
        try:
            with open('../generated_files/heatmap_info.md', 'w')  as gf:
                print('Pupil Labs :  total number of fixations: {}'.format(len(pl_x_coords)), file=gf)
                print('EyeLink    :  total number of fixations: {}'.format(len(el_x_coords)), file=gf)
                print('Pupil Labs :  all picture_ids that were shown: {}'.format(np.sort(raw_fix_count_df.query("et == 'Pupil Labs'").pic_id.unique())), file=gf)
                print('EyeLink    :  all picture_ids that were shown: {}'.format(np.sort(raw_fix_count_df.query("et == 'EyeLink'").pic_id.unique())), file=gf)
        except FileNotFoundError:
            print('file not found to save numbers...')
            import os
            print(os.getcwd())
        plt.show()






def make_heatmap(x_coords, y_coords, sigma, pic_size_horizontal, pic_size_vertical):
    '''
    returns an array to plot a heatmap of the data
    '''
    
    # make bins from - picturesize in degrees to picturesize in degrees with a stepsize of 0.01
    bins=[np.arange(-pic_size_horizontal,pic_size_horizontal,step=0.01),np.arange(-pic_size_vertical,pic_size_vertical,step=0.01)]
    
    # first make a 2d histogram
    heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=bins)
    # then use a gaussian filter for smoothing
    heatmap = gaussian_filter(heatmap, sigma=sigma)
    
    # return the edges of the heatmap in a list
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    return heatmap.T, extent



def plot_number_of_fixations(raw_fix_count_df, option=None):
    """
    investigate on the number of fixations
    """

    if option is None:
        # mean number of fixations for each subject
        mean_fixcount_per_pic = raw_fix_count_df.groupby(['et', 'subject'],as_index=False).mean()
        
        # plotting mean number of detected fixation during freeview condition for each subject
        return (ggplot(mean_fixcount_per_pic, aes(x='et', y='fix_counts')) +
                 geom_line(aes(group='subject'), color='lightblue') +
                 geom_point(color='lightblue') +
                 stat_summary(fun_data=winmean_cl_boot,color='black',size=0.8, position=position_nudge(x=0.05,y=0)) +
                 xlab("Eye Tracker") + 
                 ylab("Mean number of fixations per picture") +
                 ggtitle('Subjectwise mean number of fixations'))
                  
    
    elif option == 'violin':       
        # using violin to compare eye tracker overall
        # using raw fixation counts
        return (ggplot(raw_fix_count_df, aes(x='et', y='fix_counts')) \
                + geom_violin(aes(color='et', fill='et'), alpha = 0.25, show_legend=False) \
                + xlab("Eye Tracker") \
                + ylab('Number of fixations per picture') \
                + ggtitle('Distribution of number of fixations'))

        
    elif option == 'facet_subjects':        
        # shows number of fixations per picture for each eye tracker (facets over subjects)   
        return (ggplot(raw_fix_count_df, aes(x='et', y='fix_counts', color = 'factor(pic_id)')) \
                + geom_point(alpha=0.4) \
                + geom_line(aes(group='pic_id')) \
                + facet_grid('.~subject') \
                + xlab('Eye Tracker') \
                + ylab('Number of fixations per picture') \
                + ggtitle('EyeLink vs PupilLabs: Number of fixations for each picture')).draw()
              
    else:
        raise ValueError('You must set options to a valid option. See documentation.')
    

    
def plot_fixation_durations(raw_freeview_df, option=None):
    """
    makes a density plot to investigate on the fixation durations
    compares EyeLink and Pupil Labs in same figure
    """
    
    # set theme to default
    theme_set(mythemes.default_theme)
    
    if option is None:
        # use all detected fixations of all subjects and plot desity for each eyetracker
        # Caution: ets might have different number of detected saccades as basis!
        return (ggplot(raw_freeview_df, aes(x='duration', color='et'))
                    + geom_density()
                
                    + xlim([0,1])
                    + xlab('fixation duration [s]')
                    + ggtitle('Fixation durations'))
                
        
    elif option == 'facet_subjects':        
        # shows fixation duration densities (facets over subjects)   
        return (ggplot(raw_freeview_df, aes(x='duration', color='et'))
                + geom_density()
                + xlim([0,1])
                + xlab('fixation duration [s]')
                + facet_wrap('subject')
                + ggtitle('Fixation durations'))
            
        
    else:
        raise ValueError('You must set options to a valid option. See documentation.')
    


def plot_scanpath(etsamples, etmsgs, subject,pic_id):
    """
    plots the scanpath of the subject  into picture (picture id)
    """
    
    # set theme to default
    theme_set(mythemes.default_theme)


    # idea load msgs and samples for indicated subject
    # use function plot around event???

    print("We look at the scanpath of participant: ", subject)
    print()

    all_msgs    = etmsgs.query('subject==@subject')
    all_samples = etsamples.query('subject==@subject')


    # select only relevant columns in all_msgs
    all_msgs = all_msgs.query("condition=='FREEVIEW'").filter(items=['block', 'pic_id', 'exp_event', 'eyetracker', 'msg_time', 'trial'])


    for eyetracker in ['el','pl']:

        # we presented the pictures for 6 seconds
        # the msgs are parsed in a way that the picture_id is sent after viewing
        # therefore we subtract 6 seconds from the msg time
        el_start_time = float(all_msgs.query('(pic_id == @pic_id) & (eyetracker == @eyetracker)').msg_time.values - 6)
        el_end_time = float(all_msgs.query('(pic_id == @pic_id) & (eyetracker == @eyetracker)').msg_time.values)




        x_fix = all_samples.query('(smpl_time >= @el_start_time) & (smpl_time <= @el_end_time) & (type == "fixation") & (eyetracker == @eyetracker)').gx.values
        y_fix = all_samples.query('(smpl_time >= @el_start_time) & (smpl_time <= @el_end_time) & (type == "fixation") & (eyetracker == @eyetracker)').gy.values

        x_sac = all_samples.query('(smpl_time >= @el_start_time) & (smpl_time <= @el_end_time) & (type == "saccade") & (eyetracker == @eyetracker)').gx.values
        y_sac = all_samples.query('(smpl_time >= @el_start_time) & (smpl_time <= @el_end_time) & (type == "saccade") & (eyetracker == @eyetracker)').gy.values


        assert (len(x_fix) == len(y_fix))

        path = '/net/store/nbp/users/kgross/etcomp/experiment/stimuli/Muster'
        os.chdir(path)
        file_list = os.listdir(path)

        pic_ids_keys      = [float(id) for id in range(1,19)]
        file_names_values = file_list[0:18]
        map_id2file = dict(zip(pic_ids_keys, file_names_values))



        img = imread(map_id2file.get(pic_id))

        from scipy.misc import imresize
        img_resize = imresize(img,size=0.6)

        if eyetracker == 'pl':
            colorlist = ['blue','cyan']
        if eyetracker == 'el':
            colorlist = ['red','magenta']

        plt.scatter(x_sac, y_sac, alpha=0.5, s=10, c=colorlist[0])
        plt.scatter(x_fix, y_fix, alpha=0.5, s=10, c=colorlist[1])


    pic_size_horizontal = helper.size_px2deg(1500*0.6) 
    pic_size_vertical = helper.size_px2deg(1200*0.6) 

    plt.imshow(img_resize,alpha=0.3, extent=[-(pic_size_horizontal), (pic_size_horizontal), -(pic_size_vertical), (pic_size_vertical)])


    plt.show()

    
