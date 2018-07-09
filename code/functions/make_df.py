#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:57:55 2018

@author: kgross

GET nice DATAFRAMES


"""
 
import pandas as pd
import numpy as np
from numpy import pi
from scipy.spatial import distance

import functions.et_helper as  helper

import logging


#%% MAKE SAMPLES

def make_samples_df(etsamples):
   
    fields_to_keep = set(['smpl_time', 'gx', 'gy', 'confidence', 'pa',  'type','gx_vel','gy_vel'])
    
    fields_to_fillin = fields_to_keep - set(etsamples.columns)
    fields_to_copy =  fields_to_keep - fields_to_fillin
    
    etsamples_reduced = etsamples.loc[:,fields_to_copy]
    
    for fieldname in fields_to_fillin:
        etsamples_reduced.loc[:,fieldname] = np.nan
    
    # convert pixels into visual degrees
    # VD
    etsamples_reduced.gx = helper.px2deg(etsamples_reduced.gx, 'horizontal')
    etsamples_reduced.gy = helper.px2deg(etsamples_reduced.gy, 'vertical')
    
    return(etsamples_reduced)



def make_events_df(etevents):
    fields_to_keep = set(['blink_id', 'start_gx','start_gy','end_gx','end_gy','end_time', 'start_time', 'type', 'amplitude', 'duration', 'end_point', 'peak_velocity', 'mean_gx', 'mean_gy', 'spher_fix_rms','spher_rms','spher_amplitude'])
        
    fields_to_fillin = fields_to_keep - set(etevents.columns)
    fields_to_copy =  fields_to_keep - fields_to_fillin
    
    etevents_reduced = etevents.loc[:,fields_to_copy]
    
    for fieldname in fields_to_fillin:
        etevents_reduced.loc[:,fieldname] = np.nan
    
    return(etevents_reduced)
    
#%% MAKE EPOCHS

def make_epochs(et,msgs,td=[-2,2]):
    # formally called match_data

    # Input:    et(DataFrame)      input data of the eyetracker (has column smpl_time)
    #           msgs(DataFrame)    already parsed input messages    e.g. 'GRID element 5 pos-x 123 ...' defining experimental events (has column msg_time)
    # Output:   df for each notification,
    #           find all samples that are in the range of +-td (default timediff 2 s)
    
    # get a logger
    logger = logging.getLogger(__name__)
    
    epoched_data = pd.DataFrame()
    
    for idx,msg in msgs.iterrows():
        logger.debug(idx)
        ix = ((et['smpl_time'] - msg['msg_time'])>td[0]) & ((et['smpl_time'] - msg['msg_time'])<td[1]) # ix is a boolean (0 / 1, false / true) (this way we find all samples +-td)
        if np.sum(ix) == 0:
            logger.warning('warning, no sample found for msg %i'%(idx))
            logger.warning(msg)
            continue
        tmp= et.loc[ix]
        tmp = tmp.assign(td=tmp.smpl_time-msg['msg_time'])
    
        msg_tmp = pd.concat([msg.to_frame()]*tmp.shape[0],axis=1).T
        msg_tmp.index = tmp.index
                
        tmp = pd.concat([tmp,msg_tmp],axis=1)
        epoched_data = epoched_data.append(tmp)
                 
    return(epoched_data)
 
   
#%% Make df for LARGE GRID condition
 
def calc_horizontal_accuracy(row):
    # use absolute value of difference in angle (horizontal)
    return np.abs(row['posx'] - row['mean_gx'])

def calc_vertical_accuracy(row):
    # use absolute value of difference in angle (vertical)
    return np.abs(row['posy'] - row['mean_gy'])

def calc_3d_angle_onerow(row):
    # this is just a wrapper
    return calc_3d_angle_points(row['posx'], row['posy'], row['mean_gx'], row['mean_gy'])

def calc_3d_angle_points(x_0, y_0, x_1, y_1):
    
    # calculate the spherical angle between 2 points
    vec1 = helper.sph2cart(x_0/360*2*pi, y_0/360*2*pi)
    vec2 = helper.sph2cart(x_1/360*2*pi, y_1/360*2*pi)
    
    # pupillabs : precision = np.sqrt(np.mean(np.rad2deg(np.arccos(succesive_distances.clip(-1., 1.))) ** 2))
    cosdistance = np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))
    angle = np.arccos(np.clip(cosdistance,-1., 1.))
    angle = angle * 360/(2*pi) # radian to degree
    
    return angle


def make_large_grid_df(merged_events):
    # Input:    merged_events have info from msgs df AND event df
    #           (see add_msg_to_event in et_helper)
    
    # only large grid condition
    large_grid_events = merged_events.query('condition == "GRID"').loc[:,['type', 'end_time', 'mean_gx','duration', 'start_time', 'spher_fix_rms', 'mean_gy', 'block', 'condition', 'element', 'exp_event', 'grid_size', 'msg_time', 'posx', 'posy']]
    # use the last exp_event fixation as element 50
    stopevents = large_grid_events.query('exp_event=="stop"').assign(element=50.,grid_size=49.,posx=0,posy=0,exp_event='element')
    large_grid_events.loc[stopevents.index] = stopevents
    
    # only last fixation before new element
    large_grid_df = helper.only_last_fix(large_grid_events, next_stim = ['block', 'element'])
    
    # Accuracy
    # use absolute value of difference in angle (horizontal)
    large_grid_df['hori_accuracy'] = large_grid_df.apply(calc_horizontal_accuracy, axis=1)
    # use absolute value of difference in angle (vertical)
    large_grid_df['vert_accuracy'] = large_grid_df.apply(calc_vertical_accuracy, axis=1)
    # calculate the spherical angle
    large_grid_df['accuracy'] = large_grid_df.apply(calc_3d_angle_onerow, axis=1)
   
    return large_grid_df


   
#%% Make df for FREEVIEW condition

# TODO
def make_all_elements_grid_df(merged_events):
    # Input:    merged_events have info from msgs df AND event df
    #           (see add_msg_to_event in et_helper)
    
    # only large grid condition
    large_grid_events = merged_events.query('condition == "GRID"').loc[:,['type', 'end_time', 'mean_gx','duration', 'start_time', 'spher_fix_rms', 'mean_gy', 'block', 'condition', 'element', 'exp_event', 'grid_size', 'msg_time', 'posx', 'posy']]
    # use the last exp_event fixation as element 50
    stopevents = large_grid_events.query('exp_event=="stop"').assign(element=50.,grid_size=49.,posx=0,posy=0,exp_event='element')
    large_grid_events.loc[stopevents.index] = stopevents
    
    # only small grid before condition
    small_grid_before_events = merged_events.query('condition == "SMALLGRID_BEFORE"').loc[:,['type', 'end_time', 'mean_gx','duration', 'start_time', 'spher_fix_rms', 'mean_gy', 'block', 'condition', 'element', 'exp_event', 'grid_size', 'msg_time', 'posx', 'posy']]
    
    # only small grid after condition
    small_grid_after_events = merged_events.query('condition == "SMALLGRID_AFTER"').loc[:,['type', 'end_time', 'mean_gx','duration', 'start_time', 'spher_fix_rms', 'mean_gy', 'block', 'condition', 'element', 'exp_event', 'grid_size', 'msg_time', 'posx', 'posy']]
    

    

    # take only elements that are in small and large grid
    all_elements_df = pd.concat([large_grid_events, small_grid_before_events, small_grid_after_events], ignore_index=True)
   
    
    # only last fixation before new element
    all_elements_df = helper.only_last_fix(all_elements_df, next_stim = ['condition', 'block', 'element'])

    
    # Accuracy
    # use absolute value of difference in angle (horizontal)
    all_elements_df['hori_accuracy'] = all_elements_df.apply(calc_horizontal_accuracy, axis=1)
    # use absolute value of difference in angle (vertical)
    all_elements_df['vert_accuracy'] = all_elements_df.apply(calc_vertical_accuracy, axis=1)
    # calculate the spherical angle
    all_elements_df['accuracy'] = all_elements_df.apply(calc_3d_angle_onerow, axis=1)
   
    return all_elements_df



   
#%% Make df for FREEVIEW condition
    
def make_freeview_df(merged_freeview_events):
    # Input:    merged_events have info from msgs df AND event df
    #           (see add_msg_to_event in et_helper)
    
    
    # select only relevant columns
    all_freeview_events = merged_freeview_events.loc[:,['msg_time', 'condition', 'exp_event', 'block', 'trial', 'pic_id', 'type', 'start_time', 'end_time','duration', 'mean_gx', 'mean_gy', 'spher_fix_rms']]
    
    # select only fixations while picture was presented
    freeview_fixations_df = all_freeview_events.query("type == 'fixation' & exp_event == 'trial'")
    
    # count how many fixations per trail   in seperate dataframe
    fix_count_df = freeview_fixations_df.groupby(['block', 'trial', 'pic_id']).size().reset_index(name='fix_counts')
    
    
    return freeview_fixations_df, fix_count_df

