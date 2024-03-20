#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 19:47:14 2018

@author: kgross
"""
import functions.et_helper as  helper
from functions.et_helper import winmean_cl_boot
import functions.et_preprocess as preprocess
import functions.plotnine_theme as mythemes
import logging
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.pyplot import imread
import numpy as np
import os
import pandas as pd
from plotnine import *
from scipy.ndimage.filters import gaussian_filter
from skimage.transform import resize


def plot_heatmap(raw_freeview_df, raw_fix_count_df, only_horizontal_heatmap=True):
    """
    Make a heatmap of the freeview fixation data.

    Parameters:
    - raw_freeview_df (DataFrame): DataFrame containing freeview fixation data.
    - raw_fix_count_df (DataFrame): DataFrame containing fixation count data.
    - only_horizontal_heatmap (bool): Flag to indicate whether to display only horizontal heatmaps.

    Returns:
    - None

    Notes:
    - This function generates heatmaps and scatter plots for EyeLink and TrackPixx fixation data.
    - It calculates the mean fixation locations and displays them with specified smoothing.
    - The function can generate horizontal or 2x2 subplots based on the 'only_horizontal_heatmap' parameter.
    - Information about fixations and picture IDs is saved in a markdown file 'heatmap_info.md'.
    """

    # Calculate picture size in degrees
    # the pictures have a size of 1200 x 1500 pixels
    # factor of 0.6 as we scaled the  pictures in the matlabscript (experiment)
    # they are centered  --> divide by 2
    pic_size_horizontal = helper.size_px2deg(1500 * 0.6) / 2
    pic_size_vertical = helper.size_px2deg(1200 * 0.6) / 2

    # Extract mean fixation location data for EyeLink and TrackPixx
    tpx_x_coords = list(raw_freeview_df.query('et == "TrackPixx"').mean_gx)
    tpx_y_coords = list(raw_freeview_df.query('et == "TrackPixx"').mean_gy)
    
    el_x_coords = list(raw_freeview_df.query('et == "EyeLink"').mean_gx)
    el_y_coords = list(raw_freeview_df.query('et == "EyeLink"').mean_gy)

    # Ensure equal number of x and y gaze fixation positions
    assert(len(tpx_x_coords) == len(tpx_y_coords))
    assert(len(el_x_coords) == len(el_y_coords))

    # Define sigmas for Kernel smoothing
    # 0 : no smoothing for the scatterplot
    # 300: we selected 300 std as we want 3 degrees visual angle and have bins of size 0.01
    sigmas = [0, 300, 0, 300]

    if only_horizontal_heatmap:
        # Display horizontal heatmaps for EyeLink and TrackPixx (2 subplots)
        fig, axs = plt.subplots(1, 2)

        # Generate TrackPixx heatmap
        img, extent = make_heatmap(tpx_x_coords, tpx_y_coords, sigmas[1], pic_size_horizontal, pic_size_vertical)
        axs[0].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[0].set_aspect('equal')
        axs[0].set_title("TrackPixx Smoothing with 3 $^\circ$")

        # Generate EyeLink heatmap
        img, extent = make_heatmap(el_x_coords, el_y_coords, sigmas[3], pic_size_horizontal, pic_size_vertical)
        axs[1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[1].set_aspect('equal')
        axs[1].set_title("EyeLink Smoothing with 3 $^\circ$")

        plt.show()
        
    else:
        # Display 2x2 subplots for EyeLink and TrackPixx heatmaps and scatter plots
        fig, axs = plt.subplots(2, 2)

        # TrackPixx heatmap
        img, extent = make_heatmap(tpx_x_coords, tpx_y_coords, sigmas[1], pic_size_horizontal, pic_size_vertical)
        axs[0, 1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[0, 1].set_aspect('equal')
        axs[0, 1].set_title("TrackPixx Smoothing with 3 $^\circ$")

        # TrackPixx scatter plot
        axs[0, 0].plot(tpx_x_coords, tpx_y_coords, 'k.', markersize=5)
        axs[0, 0].set_aspect('equal')  
        axs[0, 0].set_xlim(extent[0], extent[1])
        axs[0, 0].set_ylim(extent[2], extent[3])
        axs[0, 0].set_title("TrackPixx Scatter plot")

        # EyeLink heatmap    
        img, extent = make_heatmap(el_x_coords, el_y_coords, sigmas[3], pic_size_horizontal, pic_size_vertical)
        axs[1, 1].imshow(img, extent=extent, origin='lower', cmap=cm.viridis)
        axs[1, 1].set_aspect('equal')
        axs[1, 1].set_title("EyeLink Smoothing with 3 $^\circ$")

        # EyeLink scatter plot
        axs[1 ,0].plot(el_x_coords ,el_y_coords , 'k.', markersize=5)
        axs[1 ,0].set_aspect('equal')
        axs[1 ,0].set_xlim(extent[0], extent[1])
        axs[1 ,0].set_ylim(extent[2], extent[3])
        axs[1 ,0].set_title("EyeLink Scatter plot")

         # Save information about fixations and picture IDs in a markdown file
        try:
            with open('../generated_files/heatmap_info.md', 'w') as gf:
                print('TrackPixx : total number of fixations: {}'.format(len(tpx_x_coords)), file=gf)
                print('EyeLink : total number of fixations: {}'.format(len(el_x_coords)), file=gf)
                print('TrackPixx : all picture_ids that were shown: {}'.format(np.sort(raw_fix_count_df.query("et == 'TrackPixx'").pic_id.unique())), file=gf)
                print('EyeLink : all picture_ids that were shown: {}'.format(np.sort(raw_fix_count_df.query("et == 'EyeLink'").pic_id.unique())), file=gf)
        except FileNotFoundError:
            print('File not found to save numbers...')
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
    Make a density plot to investigate fixation durations and compare EyeLink and TrackPixx data in the same figure.

    Parameters:
    - raw_freeview_df (DataFrame): DataFrame containing raw fixation data.
    - option (str): Option to specify the type of plot. Default is None.

    Returns:
    - ggplot object: A density plot comparing fixation durations for EyeLink and Pupil Labs.

    Notes:
    - This function generates a density plot to analyze fixation durations.
    - It compares fixation durations between EyeLink and Pupil Labs eye trackers.
    - If no option is provided, it plots the density for all fixations from both eye trackers.
    - The 'facet_subjects' option plots fixation duration densities with facets over subjects.
    - Ensure the DataFrame 'raw_freeview_df' contains necessary columns like 'duration', 'et', and 'subject'.
    - Adjustments to xlim and binwidth can be made for better visualization.
    """

    # Set theme to default
    theme_set(mythemes.default_theme)

    if option is None:
        # Plot density for all fixations from all subjects from both eye trackers
        # Caution: ets might have different number of detected saccades as basis!
        return (ggplot(raw_freeview_df, aes(x='duration', color='et'))
                    + geom_freqpoly(binwidth=0.025)
                    + coord_cartesian(xlim=[0, 1.5])
                    + xlab('Fixation Duration [s]')
                    + ggtitle('Fixation Durations'))

    elif option == 'facet_subjects':
        # Plot fixation duration densities with facets over subjects
        return (ggplot(raw_freeview_df, aes(x='duration', color='et'))
                + geom_density()
                + xlim([0, 1])
                + xlab('Fixation Duration [s]')
                + facet_wrap('Subject')
                + ggtitle('Fixation Durations'))

    else:
        raise ValueError('You must set options to a valid option. See documentation.')


def plot_scanpath(etsamples, etmsgs, subject, pic_id, pic_path):
    """
    Plot the scanpath of a subject onto a specified picture.

    Parameters:
        etsamples (pd.DataFrame): DataFrame containing eye tracking samples data.
        etmsgs (pd.DataFrame): DataFrame containing eye tracking messages data.
        subject (str): Subject ID for whom the scanpath is plotted.
        pic_id (int): Picture ID onto which the scanpath is plotted.

    Returns: None

    Notes:
    - This function visualizes the scanpath of a subject on a specific picture based on eye tracking data.
    - It extracts fixation and saccade data within the viewing time window of the picture presentation.
    - Since the pictures were presented for 6 seconds and the msgs are parsed in a way that 
      the picture_id is sent after viewing, we need to subtract 6 seconds from the msg time
    - The scanpath is plotted with fixations in one color and saccades in another color for each eyetracker.
    - The function resizes and overlays the picture with the scanpath for visualization.
    """
    logger = logging.getLogger(__name__)

    # Set theme to default
    theme_set(mythemes.default_theme)

    logger.warning("We look at the scanpath of participant: %s", subject)

    all_msgs = etmsgs.query('subject == @subject')
    all_samples = etsamples.query('subject == @subject')
    # select only relevant columns in all_msgs
    all_msgs = all_msgs.query("condition == 'FREEVIEW'").filter(items=['block', 'pic_id', 'exp_event', 'eyetracker', 'msg_time', 'trial'])

    for eyetracker in ['el', 'tpx']:
        et_start_time = float(all_msgs.query('(pic_id == @pic_id) & (eyetracker == @eyetracker)').msg_time.values - 6)
        et_end_time = float(all_msgs.query('(pic_id == @pic_id) & (eyetracker == @eyetracker)').msg_time.values)
        x_fix = all_samples.query('(smpl_time >= @et_start_time) & (smpl_time <= @et_end_time) & (type == "fixation") & (eyetracker == @eyetracker)').gx.values
        y_fix = all_samples.query('(smpl_time >= @et_start_time) & (smpl_time <= @et_end_time) & (type == "fixation") & (eyetracker == @eyetracker)').gy.values
        x_sac = all_samples.query('(smpl_time >= @et_start_time) & (smpl_time <= @et_end_time) & (type == "saccade") & (eyetracker == @eyetracker)').gx.values
        y_sac = all_samples.query('(smpl_time >= @et_start_time) & (smpl_time <= @et_end_time) & (type == "saccade") & (eyetracker == @eyetracker)').gy.values

        assert (len(x_fix) == len(y_fix))

        # FIXME this datapath needs to go
        # path = '/net/store/nbp/users/kgross/etcomp/experiment/stimuli/Muster'
        # os.chdir(path)
        file_list = os.listdir(pic_path)
        pic_ids_keys = [float(id) for id in range(1, 30)]
        file_names_values = file_list[0:29]
        map_id2file = dict(zip(pic_ids_keys, file_names_values))
        # foo = map_id2file.get(pic_id)
        # bar = os.path.join(pic_path, foo)
        img = imread(os.path.join(pic_path, map_id2file.get(pic_id)))
        # img_resize = resize(img, size=0.6)

        if eyetracker == 'el':
            colorlist = ['blue', 'cyan']
        if eyetracker == 'tpx':
            colorlist = ['red', 'magenta']

        plt.scatter(x_sac, y_sac, alpha=0.5, s=10, c=colorlist[0])
        plt.scatter(x_fix, y_fix, alpha=0.5, s=10, c=colorlist[1])

    pic_size_horizontal = helper.size_px2deg(1500 * 0.6) / 2
    pic_size_vertical = helper.size_px2deg(1200 * 0.6) / 2

    plt.imshow(img, alpha=0.3, extent=[-(pic_size_horizontal), pic_size_horizontal, -(pic_size_vertical), pic_size_vertical])

    # plt.imshow(img_resize, alpha=0.3, extent=[-(pic_size_horizontal), pic_size_horizontal, -(pic_size_vertical), pic_size_vertical])
    plt.show()
