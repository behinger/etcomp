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
import functions.plotnine_theme as mythemes

import functions.et_helper as  helper
from functions.et_helper import winmean,winmean_cl_boot

#%% different functions for analysing the Large Grid


def plot_accuracy_be(raw_large_grid_df, agg=[winmean,winmean,]):
    data_agg = raw_large_grid_df.groupby(['block','subject','et'],as_index=False).agg(agg[0]).groupby(['subject','et'],as_index=False).agg(agg[1])
    
    
        # plot eyetracker vs  mean accuracy over all blocks
    p = (ggplot(data_agg, aes(x='et', y='accuracy', color='subject')) 
                  +geom_line(aes(group='subject'))
                  +geom_point()
                  +stat_summary(fun_data=winmean_cl_boot,color='red',size=2)
                  +guides(color=guide_legend(ncol=40))
    )
                  
    return(p)
    
    
def plot_accuracy(raw_large_grid_df, option=None, agg_level=None, depvar = 'accuracy'):
    """
    Input:  raw df for condition
            option: None; variance_within_block 
    Output: figure that visualize the difference in accuracy btw. el and pl
    """
       
    # specify aggregators for different levels
    
    #  element level   - -   block level   - -    (subject level)
    #       mean               median                  (mean)
    
    if agg_level is None:
        # as default we use the mean over the elements (so that also elements in the periphery influence the performance)
        # and the median over the blocks (so that 'outlier blocks' do not influence the overall accuracy)
        agg_level=[winmean,winmean]
    
    # aggregate data of the large grid df
    mean_over_elements                    = raw_large_grid_df.groupby(['block','subject','et'], as_index=False).agg(agg_level[0])
    mean_over_elements_median_over_blocks = mean_over_elements.groupby(['subject','et'], as_index=False).agg(agg_level[1])
    
    
    if option is None:
        # plot eyetracker vs  mean accuracy over all blocks
        return (ggplot(mean_over_elements_median_over_blocks, aes(x='et', y=depvar)) +\
                  geom_line(aes(group='subject'), color='lightblue') +
                  geom_point(color='lightblue') +
                  stat_summary(fun_data=winmean_cl_boot,color='black',size=0.8, position=position_nudge(x=0.05,y=0)) +
                  #guides(color=guide_legend(ncol=8)) +
                  xlab("Eye Trackers") + 
                  ylab(depvar.capitalize()+" [$^\circ$]") +
                  ggtitle('Winsorized Mean Accuracies'))
        
        
    elif option == 'variance_within_block':
        return (ggplot(aes(x='et', y=depvar,color='factor(block)'), data=mean_over_elements) +
                    geom_point(alpha=0.1,data=raw_large_grid_df,position=position_dodge(width=0.7)) +
                    geom_point(position=position_dodge(width=0.7))+
                    geom_line(aes(group='block'), position= position_dodge(width=0.7)) +
                    facet_wrap('~subject',scales="free_y") + 
                    guides(color=guide_legend(ncol=8)) +
                    ggtitle('Investigating on the spread of accuracies within a block'))

    else:
        raise ValueError('You must set options to a valid option. See documentation.')


def make_table_accuracy_winmean(raw_large_grid_df, concise=False):
    """
    returns a df with the mean, median and range of all calculated accuracy values
    """
    
    # specify aggregators for different levels
    
    #  element level   - -   block level   - -    subject level
    #       mean               median                  mean
    
    # we use the median over the blocks so that 'outlier blocks' do not influence the overall accuracy
    def apply_agg_level(df,agg_level):
        block = df.groupby(['block','subject','et'], as_index=False).agg(agg_level[0])
        subject = block.groupby(['subject','et'], as_index=False).agg(agg_level[1])
        group = subject.groupby('et',as_index=False).agg(agg_level[0])
        return(block,subject,group)
    
    
    meanMedianMean_block       ,meanMedianMean_subject       ,meanMedianMean_group        =apply_agg_level(raw_large_grid_df,[np.mean, np.median, np.mean])
    meanMeanMean_block         ,meanMeanMean_subject         ,meanMeanMean_group          =apply_agg_level(raw_large_grid_df,[np.mean, np.mean,   np.mean])
    winmeanWinmeanWinmean_block,winmeanWinmeanWinmean_subject,winmeanWinmeanWinmean_group =apply_agg_level(raw_large_grid_df,[winmean, winmean,   winmean])
    
    
    acccuracy_table = pd.concat([meanMedianMean_group.assign(cumtype='meanMedianMean'),
                                meanMeanMean_group.assign(cumtype='meanMeanMean'),
                                winmeanWinmeanWinmean_group.assign(cumtype='winmeanWinmeanWinmean')
                                
                               ])
    
    # init df
    #acccuracy_table = pd.DataFrame(columns=['mean-mean-mean','mean-median-mean', 'horizontal_accuracy', 'vertical_accuracy', 'subject_min_accuracy','subject_max_accuracy', 'mean_rms'], index=['EyeLink','Pupil Labs'])

    
    #acccuracy_table.loc['EyeLink']    = pd.Series({'mean-mean-mean': mm_eyelink_data.accuracy.mean(), 'mean-median-mean': eyelink_data.accuracy.mean(),   'horizontal_accuracy': eyelink_data.hori_accuracy.mean(),  'vertical_accuracy': eyelink_data.vert_accuracy.mean(),   'subject_min_accuracy': eyelink_data.accuracy.min(),   'subject_max_accuracy': eyelink_data.accuracy.max(),   'mean_rms': eyelink_data.rms.mean()})
    #acccuracy_table.loc['Pupil Labs'] = pd.Series({'mean-mean-mean': mm_pupillabs_data.accuracy.mean(), 'mean-median-mean': pupillabs_data.accuracy.mean(), 'horizontal_accuracy': pupillabs_data.hori_accuracy.mean(),'vertical_accuracy': pupillabs_data.vert_accuracy.mean(), 'subject_min_accuracy': pupillabs_data.accuracy.min(), 'subject_max_accuracy': pupillabs_data.accuracy.max(), 'mean_rms': pupillabs_data.rms.mean()})
    
    
    # convert dtypes to floats and round results
    acccuracy_table = acccuracy_table.round(2)
    
    # only report most important columns
    if concise:
        print('to be done bene was lazy')
    #    return acccuracy_table[['mean-median-mean']].round(1) 
    
    return acccuracy_table

def make_table_accuracy(raw_large_grid_df, concise=False):
    """
    returns a df with the mean, median and range of all calculated accuracy values
    """
    
    # specify aggregators for different levels
    
    #  element level   - -   block level   - -    subject level
    #       mean               median                  mean
    
    # we use the median over the blocks so that 'outlier blocks' do not influence the overall accuracy
    agg_level=[np.mean, np.median, np.mean]
    
    # aggregate data of the large grid df  according to agg_level list  
    mean_over_elements = raw_large_grid_df.groupby(['block','subject','et'], as_index=False).agg(agg_level[0])
    mean_over_elements_median_over_blocks = mean_over_elements.groupby(['subject','et'], as_index=False).agg(agg_level[1])   

    # separate the data for each Eyetracker
    # we get subjectwise median overblocks mean over lements df
    eyelink_data = mean_over_elements_median_over_blocks.query('et == "EyeLink"')
    pupillabs_data = mean_over_elements_median_over_blocks.query('et == "Pupil Labs"')
       
    # get mean-mean aggregated data
    mm_eyelink_data   = raw_large_grid_df.groupby(['block','subject','et'], as_index=False).agg(np.mean).groupby(['subject','et'], as_index=False).agg(np.mean).query('et == "EyeLink"')
    mm_pupillabs_data = raw_large_grid_df.groupby(['block','subject','et'], as_index=False).agg(np.mean).groupby(['subject','et'], as_index=False).agg(np.mean).query('et == "Pupil Labs"')

    # init df
    acccuracy_table = pd.DataFrame(columns=['mean-mean-mean','mean-median-mean', 'horizontal_accuracy', 'vertical_accuracy', 'subject_min_accuracy','subject_max_accuracy', 'mean_rms'], index=['EyeLink','Pupil Labs'])

    # just calculating the mean, median and range:
    # as there might be elements where we didn"t detect a fixation, 
    # we first calculate the mean accuracy over the elements for each subject and then take the mean over all subjects
    # TODO !! careful with the median : taking the mean for the blocks in the subject, but the median over the subjects!!
    acccuracy_table.loc['EyeLink']    = pd.Series({'mean-mean-mean': mm_eyelink_data.accuracy.mean(), 'mean-median-mean': eyelink_data.accuracy.mean(),   'horizontal_accuracy': eyelink_data.hori_accuracy.mean(),  'vertical_accuracy': eyelink_data.vert_accuracy.mean(),   'subject_min_accuracy': eyelink_data.accuracy.min(),   'subject_max_accuracy': eyelink_data.accuracy.max(),   'mean_rms': eyelink_data.rms.mean()})
    acccuracy_table.loc['Pupil Labs'] = pd.Series({'mean-mean-mean': mm_pupillabs_data.accuracy.mean(), 'mean-median-mean': pupillabs_data.accuracy.mean(), 'horizontal_accuracy': pupillabs_data.hori_accuracy.mean(),'vertical_accuracy': pupillabs_data.vert_accuracy.mean(), 'subject_min_accuracy': pupillabs_data.accuracy.min(), 'subject_max_accuracy': pupillabs_data.accuracy.max(), 'mean_rms': pupillabs_data.rms.mean()})
    
    
    # convert dtypes to floats and round results
    acccuracy_table = acccuracy_table.astype('float').round(2)
    
    # only report most important columns
    if concise:
        return acccuracy_table[['mean-median-mean']].round(1) 
    
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
    
    
    example promt LARGE_GRID.display_fixations(raw_large_grid_df, option='offset', greyscale=True)

    Please select a subject: VP4

    Please select a block: 1
    
    returns plot
    
    """
    
    # only if offset option you need to ask user to specify    
    if option == 'offset':
    # use terminal promt to select one subject
    # do not enter with "" !
            if input_subject is None:
                input_subject = [input("Please select a subject: ")]
            if input_block is None:
                input_block = [input("Please select a block: ")]           
            
    
    # make separate figure for each eyetracker
    for eyetracker in [["EyeLink"], ["Pupil Labs"]]:
        et_grouped_elem_pos = raw_large_grid_df.query('et==@eyetracker')    
        
       
        if option == 'fixations':
            # visualize fixations
            # subjects vs blocks
            # new window for each eyetracker
            
            # save old theme and set the one for fixation plotting
            old_theme = theme_get()
            theme_set(mythemes.display_fixation_theme)
            
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
                p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' + str(eyetracker)[2:-2] +' displayed_fixations.png'), height=10, width=13, units = 'in', dpi=500)
                
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
                
            
            # restore old theme
            theme_set(old_theme)
            
 
        
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
                p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' + str(eyetracker)[2:-2] +' fixation_offset2.png'), height=5, width=10, units = 'in', dpi=400)
                
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
    return((ggplot(raw_large_grid_df, aes(x='mean_gx-posx', y='mean_gy-posy', color='np.sqrt(posx**2+posy**2)'))
            #+ geom_point(alpha=0.01)
            +stat_ellipse(level=0.90)
            +stat_ellipse(level=0.70)
            +stat_ellipse(level=0.50)
            +stat_ellipse(level=0.30)
            +stat_ellipse(level=0.10)
            # displayed elements
            + annotate("point",x=0, y=0, color='black', shape = 'x')
            + facet_wrap("~et")+coord_fixed(xlim=[-4,4],ylim=[-4,4])

    ))
#
# Density comparison: Fails because I don't know how to standardize properly
#raw_large_grid_df.loc[:,'x_center']= raw_large_grid_df.posx - raw_large_grid_df.mean_gx
#raw_large_grid_df.loc[:,'y_center']= raw_large_grid_df.posy - raw_large_grid_df.mean_gy
#(ggplot(raw_large_grid_df.query("abs(x_center)<10 & abs(y_center)<10&eyetracker=='pl'"), aes(x='x_center', y='y_center',group='et',color='et',fill='et'))
#             + geom_density_2d(levels=20)
            # displayed elements
            #+ annotate("point",x=0, y=0, color='black', shape = 'x')
#)


    

##%% SAVE the plot in repository
## TODO: make this more universal and move it to et_helper
#
#plotname = 'GRID_' + et + '_' + subject
#gridplot.save(filename=plotname, format=None, path='/net/store/nbp/users/kgross/etcomp/plots', dpi=600, verbose=True)


#