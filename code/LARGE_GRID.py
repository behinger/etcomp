#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 18:59:38 2018

@author: kgross
"""


import functions.add_path

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *
# specify costumed minimal theme
import functions.plotnine_theme

import functions.et_helper as  helper


#%% different functions for analysing the Large Grid


def plot_accuracy_be(raw_large_grid_df, agg=[np.mean,np.median]):
    data_agg = raw_large_grid_df.groupby(['block','subject','et'],as_index=False).agg(agg[0]).groupby(['subject','et'],as_index=False).agg(agg[1])
    
    
        # plot eyetracker vs  mean accuracy over all blocks
    p = (ggplot(data_agg, aes(x='et', y='accuracy', color='subject')) 
                  +geom_line(aes(group='subject'))
                  +geom_point()
                  +stat_summary(color='red',size=2)
                  +guides(color=guide_legend(ncol=40))
    )
                  
    return(p)
    
    
def plot_accuracy(raw_large_grid_df, option=None):
    """
    Input:  raw df for condition
            facets: None, 'subjects', 
    Output:  ? figure(s) that visualize the difference in accuracy btw. el and pl
    """
    
    # get data grouped
    mean_for_each_subject_large_grid_df = helper.group_to_level_and_take_mean(raw_large_grid_df, lowestlevel='subject')
    mean_for_each_block_large_grid_df =  helper.group_to_level_and_take_mean(raw_large_grid_df, lowestlevel='block')
    
    
    if option is None:
        # plot eyetracker vs  mean accuracy over all blocks
        (ggplot(mean_for_each_subject_large_grid_df, aes(x='et', y='accuracy', color='subject')) +\
                  geom_line(aes(group='subject')) +\
                  geom_point() +\
                  guides(color=guide_legend(ncol=40)) +\
            
            ggtitle('Mean spherical accuracy in visual degrees over all blocks for each subject')).draw()
        
    elif option == 'facet_subjects':
        # make facets over subjects
        # investigate how mean accuracy is changes for different subjects
        (ggplot(mean_for_each_subject_large_grid_df, aes(x='et', y='accuracy', color='subject')) +
                  geom_line(aes(group='subject')) +
                  geom_point() +
                  guides(color=guide_legend(ncol=40)) +
                  facet_grid('.~subject')+
                  ggtitle('Spherical accuracy in visual degrees')).draw()
        
        
    elif option == 'dodge':
        # TODO: polish
        # Here: Learn how to use stat summary          
        (ggplot(aes(x='et', y='accuracy',color='block'), data=mean_for_each_block_large_grid_df) +
                geom_point(alpha=0.1,data=raw_large_grid_df,position=position_dodge(width=0.7)) +
                geom_point(position=position_dodge(width=0.7))+
                geom_line(aes(group='block'), position=position_dodge(width=0.7)) +
                facet_wrap('~subject',scales="free_y") + 
                guides(color=guide_legend(ncol=40)) +
                ggtitle('think of informative title')).draw()


    else:
        raise ValueError('You must set options to a valid option. See documentation.')



def make_table_accuracy(raw_large_grid_df):
    """
    returns a df with the mean, median and range of all calculated accuracy values
    """
    
    acccuracy_table = pd.DataFrame(columns=['mean','median', 'horizontal_mean', 'vertical_mean', 'subject_min_accuracy','subject_max_accuracy', 'mean_rms'], index=['EyeLink','Pupil Labs'])
   
    # just calculating the mean, median and range:
    # as there might be elements where we didn"t detect a fixation, 
    # we first calculate the mean accuracy for each subject and then take the mean over all subjects

    # get a grouped df (grouped by et and subject)
    mean_for_each_subject_large_grid_df = helper.group_to_level_and_take_mean(raw_large_grid_df, 'subject')
    
    # separate the data for each Eyetracker
    eyelink_data = mean_for_each_subject_large_grid_df.query('et == "EyeLink"')
    pupillabs_data = mean_for_each_subject_large_grid_df.query('et == "Pupil Labs"')
    

    # TODO !! careful with the median : taking the mean for the blocks in the subject, but the median over the subjects!!
    acccuracy_table.loc['EyeLink']    = pd.Series({'mean': eyelink_data.accuracy.mean(),   'median': eyelink_data.accuracy.median(),   'horizontal_mean': eyelink_data.hori_accuracy.median(),  'vertical_mean': eyelink_data.vert_accuracy.median(),   'subject_min_accuracy': eyelink_data.accuracy.min(),   'subject_max_accuracy': eyelink_data.accuracy.max(),   'mean_rms': eyelink_data.rms.mean()})
    acccuracy_table.loc['Pupil Labs'] = pd.Series({'mean': pupillabs_data.accuracy.mean(), 'median': pupillabs_data.accuracy.median(), 'horizontal_mean': pupillabs_data.hori_accuracy.median(),'vertical_mean': pupillabs_data.vert_accuracy.median(), 'subject_min_accuracy': pupillabs_data.accuracy.min(), 'subject_max_accuracy': pupillabs_data.accuracy.max(), 'mean_rms': pupillabs_data.rms.mean()})


    return acccuracy_table




def compare_accuracy_components(raw_large_grid_df, display_precision=False):
    """
    comparing horizontal, vertical and combined spherical agnle accuracy and optionally precision [rms]
    """
    
    # get data grouped
    mean_for_each_subject_large_grid_df = helper.group_to_level_and_take_mean(raw_large_grid_df, lowestlevel='subject')
    
    # select if you want to see precision/rms as well
    if display_precision:
        # investigate on accuracy and precision measures
        mean_for_each_subject_large_grid_df = mean_for_each_subject_large_grid_df.loc[:,['et', 'subject','accuracy', 'hori_accuracy', 'vert_accuracy','rms']]
    else:
        # only investigate on accuracy measures
        mean_for_each_subject_large_grid_df = mean_for_each_subject_large_grid_df.loc[:,['et', 'subject','accuracy', 'hori_accuracy', 'vert_accuracy']]
        
    # use melt to investigate on different components
    melted_measures = mean_for_each_subject_large_grid_df.melt(id_vars=['et', 'subject'], var_name='measure')
    
    # compare accuracy and precision measure (mean over all blocks) for each subject 
    (ggplot(melted_measures, aes(x='et', y='value', color='measure')) +
              geom_line(aes(group='measure')) +
              geom_point() +
              guides(color=guide_legend(ncol=40)) +
              facet_grid('.~subject')+
              ggtitle('Investigating on performance measures (mean for each subject over all blocks)')).draw()





def display_fixations(raw_large_grid_df, option='fixations', greyscale=False, input_subject=None,input_block=None):
    """
    Displaying accuracy on grid points
    
    options are: 'fixations', 'accuracy_for_each_element', 'precision_for_each_element' and 'offset'
    
    returns plot
    
    """
    
    # only if offset option you need to ask user to specify    
    if option == 'offset':
    # use terminal promt to select one subject
    # do not enter with "" !
            if input_subject is None:
                input_subject = [input("Please select a subject: ")]
            if input_block is None:
                input_block = [int(input("Please select a block: "))]           
            
    
    # make separate figure for each eyetracker
    for eyetracker in [['EyeLink'], ['Pupil Labs']]:
        et_grouped_elem_pos = raw_large_grid_df.query('et==@eyetracker')    
        
       
        if option == 'fixations':
            # visualize fixations
            # subjects vs blocks
            # new window for each eyetracker
            
            
            if greyscale:
                # no colors for position of element points
                p = (ggplot(aes(x='mean_gx', y='mean_gy'), data= et_grouped_elem_pos) +
                    geom_point(size=1.3, alpha=0.6,  show_legend=False) + 
                    # caution: limiting the axis, could cut off fixations from plot
                    coord_fixed(ratio=1, xlim=(-40.0,40.0), ylim=(-20.0,20.0)) +
                    facet_grid('block~subject', labeller=lambda x: (("subject " if x.startswith('VP') else "block ") + x))+
                    xlab("Mean horizontal fixation position [$^\circ$]") + 
                    ylab("Mean vertical fixation position [$^\circ$]") +
                    ggtitle(str(eyetracker)[2:-2] + ':  Large Grid - subjects vs block -'))
                p.draw()
                # save for teatime as png
                p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' + str(eyetracker)[2:-2] +' displayed_fixations.png'), height=15, width=15, units = 'in', dpi=1000)
                
            else:
                # color of element depends on the position of the true target element
                (ggplot(aes(x='mean_gx', y='mean_gy', color='factor(posx * posy)'), data= et_grouped_elem_pos) +
                    geom_point(show_legend=False) + 
                    # caution: limiting the axis, could cut off fixations from plot
                    coord_fixed(ratio=1, xlim=(-40.0,40.0), ylim=(-20.0,20.0)) +
                    facet_grid('block~subject', labeller=lambda x: (("subject " if x.startswith('VP') else "block ") + x))+
                    xlab("Mean horizontal fixation position [$^\circ$]") + 
                    ylab("Mean vertical fixation position [$^\circ$]") +
                    ggtitle(str(eyetracker)[2:-2] + ':  Large Grid - subjects vs block -')).draw()
 
        
        elif option == 'accuracy_for_each_element':        
            # look which grid points have higher/lower accuracy
            # takes the mean over all blocks for one element
            # visualize this by scaling  the size of the grid point
            
            # use a groupby to take the mean over all blocks
            (ggplot(aes(x='posx', y='posy', size='accuracy'), data=et_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +
                    geom_point() +
                    facet_wrap('~subject')+
                    ggtitle(str(eyetracker)[2:-2]+': Accuracy visiualized by size of grid points')).draw()
            
        
        elif option == 'precision_for_each_element':                
            # look which grid points have higher/lower precision
            # takes the mean over all blocks for one element
            # visualize this by scaling the size of the grid point
            
            # use a groupby to take the mean over all blocks
            (ggplot(aes(x='posx', y='posy', size='rms'), data=et_grouped_elem_pos.groupby(['subject','posx', 'posy']).mean().reset_index(level=['subject','posx', 'posy'])) +
                    geom_point() +
                    facet_wrap('~subject')+
                    ggtitle(str(eyetracker)[2:-2] +': Precision visiualized by size of grid points')).draw()
            
         
        elif option == 'offset':
            # mean_fix vs grid point elements
            # plots for only one specific subject and specific block
            specific_subject_df = raw_large_grid_df.query('et == @eyetracker & subject == @input_subject & block == @input_block')
                      
            if greyscale:
                # no colors for position of element points
                p = (ggplot(specific_subject_df, aes(x='mean_gx', y='mean_gy'))
                        + geom_point(size=2, alpha=0.8, show_legend=False)
                        # displayed elements
                        + geom_point(specific_subject_df, aes(x='posx', y='posy'), alpha=0.5, size=3.5, shape = 'x', show_legend=False)
                        # caution: limiting the axis, could cut off fixations from plot
                        + coord_fixed(ratio=1, xlim=(-38.0,38.0), ylim=(-17.0,17.0))
                        + xlab("Mean horizontal fixation position [$^\circ$]") 
                        + ylab("Mean vertical fixation position [$^\circ$]") 
                        + ggtitle(str(eyetracker)[2:-2] + ': Mean fixation position vs displayed element position'))
                p.draw()
                # save for teatime as png
                p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' + str(eyetracker)[2:-2] +' fixation_offset2.png'), height=5, width=10, units = 'in', dpi=1000)
                
            else:
                # color of element depends on the position of the true target element
                (ggplot(specific_subject_df, aes(x='mean_gx', y='mean_gy', color='factor(posx*posy)'))
                        + geom_point(show_legend=False)
                        # displayed elements
                        + geom_point(specific_subject_df, aes(x='posx', y='posy', color='factor(posx*posy)'), shape = 'x', show_legend=False)
                        # caution: limiting the axis, could cut off fixations from plot
                        + coord_fixed(ratio=1, xlim=(-38.0,38.0), ylim=(-17.0,17.0))
                        + xlab("Mean horizontal fixation position [$^\circ$]") 
                        + ylab("Mean vertical fixation position [$^\circ$]") 
                        + ggtitle(str(eyetracker)[2:-2] + ': Mean fixation position vs displayed element position')).draw()


        else:
            raise ValueError('You must set option to a valid string. See documentation.')
        

def display_fixation_centered(raw_large_grid_df,input_subject=None,input_block=None):   
    # plots for only one specific subject and specific block
    if input_subject is not None:
        raw_large_grid_df = raw_large_grid_df.query('subject == @input_subject')
    if input_block is not None:
        raw_large_grid_df = raw_large_grid_df.query('block == @input_block')
        # mean_fix vs grid point elements
    return((ggplot(raw_large_grid_df, aes(x='posx-mean_gx', y='posy-mean_gy', color='np.sqrt(posx**2+posy**2)'))
            + geom_point(alpha=0.1)
            # displayed elements
            + annotate("point",x=0, y=0, color='black', shape = 'x')
            + facet_wrap("~et")
    ))


    

##%% SAVE the plot in repository
## TODO: make this more universal and move it to et_helper
#
#plotname = 'GRID_' + et + '_' + subject
#gridplot.save(filename=plotname, format=None, path='/net/store/nbp/users/kgross/etcomp/plots', dpi=600, verbose=True)
