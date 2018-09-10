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
import functions.plotnine_theme as mythemes

import functions.et_helper as  helper

import logging




def plot_heatmap(raw_freeview_df,raw_fix_count_df):
    """
    Make a heatmap of the freeview fixation df
    """
    
    # the pictures have a size of 1200 x 1500 pixels
    # factor of 0.6 as we scaled the  pictures in the matlabscript (experiment)
    # they are centered  --> divide by 2
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
        print('Pupil Labs :  all picture_ids that were shown: {}'.format(np.sort(raw_fix_count_df.query("et == 'Pupil Labs'").pic_id.unique())), file=gf)
        print('EyeLink    :  all picture_ids that were shown: {}'.format(np.sort(raw_fix_count_df.query("et == 'EyeLink'").pic_id.unique())), file=gf)

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
                 stat_summary(color='black',size=0.8, position=position_nudge(x=0.05,y=0)) +
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
    

    
    

def plot_histogram(raw_fix_count_df):
    #TODO  
    pass


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
    


#
#def plot_saccade_amplitudes(option=None):
#    """
#    TODO
#    """
#
#    if option is None:
#        
#        from functions.et_make_df import make_epochs
#        
#        condquery = 'condition == "FREEVIEW" & exp_event=="trial"'
#        td = [-0.2, 6]
#        elepochs_fv = make_epochs(elsamples,elmsgs.query(condquery), td=td)
#        plepochs_fv= make_epochs(plsamples,plmsgs.query(condquery), td=td)
#        
#        
#        
#        etevents= pd.concat([elevents.assign(eyetracker='eyelink'),plevents.assign(eyetracker='pupillabs')],ignore_index=True)
#        
#        #Saccadeparameters
#        ggplot(etevents.query('type=="saccade"'),aes(x='amplitude',color='eyetracker')) + geom_density() + xlab('amplitude [degrees]') + ggtitle('Saccadeparameters')
#        
#        
#    else:
#        raise ValueError('You must set options to a valid option. See documentation.')
# 
    
#    
#def plot_main_sequence():
#    """
#    TODO
#    """
#
#    if option is None:
#
#
#        etevents= pd.concat([elevents.assign(eyetracker='eyelink'),plevents.assign(eyetracker='pupillabs')],ignore_index=True)    
#        
#        # main sequence
#        # install scikit-misc
#        ggplot(etevents.query('type=="saccade"'),aes(x='np.log10(peak_velocity)',y='np.log10(amplitude)',color='eyetracker'))+stat_smooth(method='loess') + ggtitle('main sequence')
#        
#        
#        
#    else:
#        raise ValueError('You must set options to a valid option. See documentation.')
# 
#    