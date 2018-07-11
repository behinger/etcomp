#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 19:47:14 2018

@author: kgross
"""


import functions.add_path
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from scipy.ndimage.filters import gaussian_filter

from plotnine import *
# specify costumed minimal theme
import functions.plotnine_theme

import functions.et_helper as  helper

import logging




def plot_heatmap(raw_freeview_df):
    """
    Make a heatmap of the freeview fixation df
    """
    
    # the pictures have a size of 1200 x 1500 pixels
    # they are centered  --> therefore divide by 2
    # TODO ask again why factor of 0.6 ??
    pic_size_horizontal = helper.size_px2deg(1500*0.6) / 2
    pic_size_vertical = helper.size_px2deg(1200*0.6) / 2
    
    
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
    axs[1,1].set_title("EyeLink Smoothing with 3 $^\circ$")
    
    # EyeLink scatterplot
    axs[1,0].plot(el_x_coords, el_y_coords, 'k.', markersize=5)
    axs[1,0].set_aspect('equal')
    axs[1, 0].set_xlim(extent[0], extent[1])
    axs[1, 0].set_ylim(extent[2], extent[3])
    axs[1,0].set_title("EyeLink Scatter plot")


    # put info into generated files
    with open('../generated_files/heatmap_info.md', 'w')  as gf:
        print('Pupil Labs :  total number of fixations: {}'.format(len(pl_x_coords)), file=gf)
        print('EyeLink    :  total number of fixations: {}'.format(len(el_x_coords)), file=gf)

    
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
        mean_for_each_subject_df = helper.group_to_level_and_take_mean(raw_fix_count_df, lowestlevel='subject').drop('pic_id', axis=1)
        
        # plotting mean number of detected fixation during freeview condition for each subject
        (ggplot(mean_for_each_subject_df, aes(x='et', y='fix_counts', color='subject')) +
             geom_line(aes(group='subject')) +
             geom_point() +
             guides(color=guide_legend(ncol=40)) +
             ggtitle('Mean number of fixations over all pictures for each subject')).draw()
              
    
    elif option == 'eyetracker':       
        # using boxplot to compare eye tracker overall
        (ggplot(raw_fix_count_df, aes(x='et', y='fix_counts')) \
                + geom_boxplot(aes(fill='et'), color='k', alpha=0.2, outlier_color='r', outlier_size=1.5, show_legend=False) \
                + ylab('Number of fixations per picture') \
                + ggtitle('EyeLink vs PupilLabs: Number of fixations per picture per subject')).draw()

        # using violin to compare eye tracker overall
        (ggplot(raw_fix_count_df, aes(x='et', y='fix_counts')) \
                + geom_violin(aes(color='et', fill='et'), alpha = 0.25, show_legend=False) \
                + xlab('Eyetracker') \
                + ylab('Number of fixations') \
                + ggtitle('EyeLink vs PupilLabs: Number of fixations')).draw()

        
    elif option == 'subjects':        
        # shows number of fixations per picture for each eye tracker (facets over subjects)   
        (ggplot(raw_fix_count_df, aes(x='et', y='fix_counts', color = 'factor(pic_id)')) \
                + geom_point(alpha=0.4) \
                + geom_line(aes(group='pic_id')) \
                + guides(color=guide_legend(ncol=40)) \
                + facet_grid('.~subject') \
                + xlab('Eyetracker') \
                + ylab('Number of fixations') \
                + ggtitle('EyeLink vs PupilLabs: Number of fixations for each picture')).draw()
              
    else:
        raise ValueError('You must set options to a valid option. See documentation.')
    

    
    

def plot_histogram(raw_fix_count_df):
    #TODO
    pass


               
#%% main sequence
    
#!!!!!!!!SACCADES!!!!!!!!!!!!!

# look at be_sync for help