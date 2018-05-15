#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
import math
import time

import os,sys,inspect

import matplotlib.pyplot as plt
from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import functions.nbp_pupilhelper as nbp_pl
import functions.etcomp_parse as parse
import functions.pl_detect_blinks as pl_detect_blinks
# import functions.pl_surface as pl_surface

# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib


#%% PUPILLABS

def raw_pl_data(subject, datapath='/net/store/nbp/projects/etcomp/pilot'):
    # Input:    subjectname, datapath
    # Output:   Returns pupillabs dictionary
    
    filename = os.path.join(datapath,subject,'raw')

    # with dict_keys(['notifications', 'pupil_positions', 'gaze_positions'])
    # where each value is a list that contains a dictionary
    original_pldata = pl_file_methods.load_object(os.path.join(filename,'pupil_data'))
    
    # 'notification'
    # dict_keys(['record', 'subject', 'timestamp', 'label', 'duration'])
    
    # 'pupil_positions'
    # dict_keys(['diameter', 'confidence', 'method', 'norm_pos', 'timestamp', 'id', 'topic', 'ellipse'])
    
    # 'gaze_positions'
    # dict_keys(['base_data', 'timestamp', 'topic', 'confidence', 'norm_pos'])
        # where 'base_data' has a dict within a list 
        # dict_keys(['diameter', 'confidence', 'method', 'norm_pos', 'timestamp', 'id', 'topic', 'ellipse'])
        # where 'normpos' is a list (with horizon. and vert. component)
        
    return original_pldata


def preprocess_pl(subject, recalculate=True, save=False, date=time.strftime, datapath='/net/store/nbp/projects/etcomp/pilot', recalib=False, surfaceMap = False):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
    #           recalculate      (boolean) if False, then take the csv file and take them as dfs 
    #           save             (boolean) if True, then save dfs as csv files in preprocessed folder
    #           recalib:
    #           surfaceMap:
    # Output:   Returns 2 dfs (plsamples and plmsgs)

    assert(type(subject)==str)
    # filepath for preprocessed folder
    preprocessed_path = os.path.join(datapath, subject, 'preprocessed')

    
    # load and preprocess data from raw data files
    if recalculate:
        
        # Get samples df
        original_pldata = raw_pl_data(subject, datapath)
    
        # recalibrate data
        if recalib:
            original_pldata['gaze_positions'] = nbp_recalib.nbp_recalib(original_pldata)
            
        if surfaceMap:
            folder= os.path.join(datapath,subject,'raw')
            tracker = pl_surface.map_surface(folder)   
            gaze_on_srf  = pl_surface.surface_map_data(tracker,original_pldata['gaze_positions'])
            original_pldata['gaze_positions'] = gaze_on_srf
            
    
        # use pupilhelper func to make samples df (confidence, gx, gy, smpl_time, diameter)
        pldata = nbp_pl.gaze_to_pandas(original_pldata['gaze_positions'])
        # sort according to smpl_time
        pldata.sort_values('smpl_time',inplace=True)
        
        # add Blink information to pldata
        pldata_blink = pl_detect_blinks.pupil_detect_blinks(pldata)

        # get the nice samples df
        plsamples = make_samples_df(pldata_blink) # XXX extended_samples
        
    
        # Get msgs df      
        # make a list of gridnotes that contain all notifications of original_pldata if they contain 'label'
        gridnotes = [note for note in original_pldata['notifications'] if 'label' in note.keys()]
        plmsgs = pd.DataFrame();
        for note in gridnotes:
            msg = parse.parse_message(note)
            if not msg.empty:
                plmsgs = plmsgs.append(msg, ignore_index=True)
        
        
        # save preprocessed dataframes into csv files
        if save:
            # create new folder if there is none
            if not os.path.exists(preprocessed_path):
                os.makedirs(preprocessed_path)
    
            # dump samples / msgs df in csv
            filename_plsamples = str(time.strftime("%Y-%m-%d")) + '_plsamples.csv'
            filename_plmsgs = str(time.strftime("%Y-%m-%d")) + '_plmsgs.csv'
            plsamples.to_csv(os.path.join(preprocessed_path, filename_plsamples), index=False)
            plmsgs.to_csv(os.path.join(preprocessed_path, filename_plmsgs), index=False)
        
        return plsamples, plmsgs
    
    
    # load preprocessed data from csv file
    # (from folder preprocessed)
    else:
        try:
            filename_plsamples = str(date) + '_plsamples.csv'
            filename_plmsgs = str(date) + '_plmsgs.csv'
            plsamples = pd.read_csv(os.path.join(preprocessed_path,filename_plsamples))
            plmsgs = pd.read_csv(os.path.join(preprocessed_path,filename_plmsgs))
        except FileNotFoundError as e:
            print(e)
            raise('Error: Could not read file')
        return plsamples, plmsgs





  
#%% EYELINK

def preprocess_el(subject, recalculate=True, save=False, date=time.strftime("%Y-%m-%d"), datapath='/net/store/nbp/projects/etcomp/pilot'):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
    # Output:   Returns list of 2 el df (elsamples, elmsgs)

    assert(type(subject)==str)
    # filepath for preprocessed folder
    preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
    
    # Load edf
    filename = os.path.join(datapath,subject,'raw')
    
    
    # load and preprocess data from raw data files
    if recalculate:
                
        # elsamples:  contains individual EL samples
        # elevents:   contains fixation and saccade definitions
        # elnotes:    contains notes (meta data) associated with each trial
        elsamples, elevents, elnotes = edf.pread(os.path.join(filename,findFile(filename,'.EDF')[0]), trial_marker=b'')
  
        # Convert to same units
        # change to seconds to be the same as pupil
        elsamples['smpl_time'] = elsamples['time']/1000 
        elnotes['msg_time'] = elnotes['trialid_time']/1000
        elnotes = elnotes.drop('trialid_time',axis=1)  
        elevents['msg_time'] = elevents['time']/1000
        elevents['start'] = elevents['start']/1000     
        elevents['end'] = elevents['end']/1000             
        
        # detect Blink Samples
        # use blink column in elevents to mark all samples that are recorded during blink
        # filter all rows where blink==True
        ix_blink = elevents.blink==True
        df_only_blinks = elevents.loc[ix_blink]
        # we are only interested in when the blink started and ended
        df_only_blinks = df_only_blinks.loc[:, ['start', 'end', 'blink']]
        
        # create column blink (boolean) in elsamples
        elsamples['is_blink'] = int(False)
        for bindex,brow in df_only_blinks.iterrows():
            # get index of all samples that are +- 100 ms of a detected blink
            ix =  (elsamples.smpl_time>=(brow['start']-float(0.1))) & (elsamples.smpl_time<(brow['end']+float(0.1)))
            # mark them as blink
            elsamples.loc[ix, 'is_blink'] = int(True)
        
 
        # counts up the blink_id
        # Pure Magic
        elsamples['blink_id'] = (elsamples['is_blink'] * (elsamples['is_blink'].diff()==1).cumsum())


     
        # for horizontal gaze component
        # Idea: Logical indexing
        ix_left = elsamples.gx_left  != -32768 
        ix_right = elsamples.gx_right != -32768
    
        # TODO: use bad sample removal first, as we need NaN info to set pa
        # take the pupil area pa of the recorded eye
        # set pa to NaN instead of 0  or -32768
        elsamples.loc[elsamples['pa_right'] == 0,'pa_right'] = np.nan
        elsamples.loc[~ix_right,'pa_right'] = np.nan
        elsamples.loc[elsamples['pa_left'] == 0,'pa_left'] = np.nan
        elsamples.loc[~ix_left,'pa_left'] = np.nan
        
        # add pa column that takes the value that is not NaN
        ix_left  = ~np.isnan(elsamples.pa_left)
        ix_right = ~np.isnan(elsamples.pa_right)
        
        # init with nan
        elsamples['pa'] = np.nan
        
        elsamples.loc[ix_left, 'pa'] = elsamples.pa_left[ix_left]
        elsamples.loc[ix_right,'pa'] = elsamples.pa_right[ix_right]
        
        
        # Determine which eye was recorded

        ix_left = elsamples.gx_left  != -32768 
        ix_right = elsamples.gx_right != -32768
    
        if (np.mean(ix_left | ix_right)<0.99):
            raise NameError('In more than 1 % neither left or right data')
            
        
        # for horizontal gaze component    
        elsamples.loc[ix_left,'gx']       = elsamples.gx_left[ix_left]
        elsamples.loc[ix_right,'gx']      = elsamples.gx_right[ix_right]
    
        # for horizontal gaze velocity component
        elsamples.loc[ix_left,'gx_vel']       = elsamples.gxvel_left[ix_left]
        elsamples.loc[ix_right,'gx_vel']      = elsamples.gxvel_right[ix_right]
        
        
        # for vertical gaze component
        ix_left = elsamples.gy_left  != -32768 
        ix_right = elsamples.gy_right != -32768
        
        elsamples.loc[ix_left,'gy'] = elsamples.gy_left[ix_left]
        elsamples.loc[ix_right,'gy'] = elsamples.gy_right[ix_right]
        
        # for vertical gaze velocity component
        elsamples.loc[ix_left,'gy_vel']       = elsamples.gyvel_left[ix_left]
        elsamples.loc[ix_right,'gy_vel']      = elsamples.gyvel_right[ix_right]
        
        
        # "select" relevant columns
        elsamples = make_samples_df(elsamples)
                
        
        # Parse EL msg
        elmsgs = elnotes.apply(parse.parse_message,axis=1)
        elmsgs = elmsgs.drop(elmsgs.index[elmsgs.isnull().all(1)])
        
        # save preprocessed dataframes into csv files
        if save:
            # create new folder if there is none
            if not os.path.exists(preprocessed_path):
                os.makedirs(preprocessed_path)
    
            # dump samples / msgs df in csv
            filename_elsamples = str(time.strftime("%Y-%m-%d")) + '_elsamples.csv'
            filename_elmsgs = str(time.strftime("%Y-%m-%d")) + '_elmsgs.csv'
            elsamples.to_csv(os.path.join(preprocessed_path, filename_elsamples), index=False)
            elmsgs.to_csv(os.path.join(preprocessed_path, filename_elmsgs), index=False)
        
        return elsamples, elmsgs
    
    # load preprocessed data from csv file
    # (from folder preprocessed)
    else:
        try:
            filename_elsamples = str(date) + '_elsamples.csv'
            filename_elmsgs = str(date) + '_elmsgs.csv'
            elsamples = pd.read_csv(os.path.join(preprocessed_path,filename_elsamples))
            elmsgs = pd.read_csv(os.path.join(preprocessed_path,filename_elmsgs))
        except FileNotFoundError as e:
            print(e)
            raise('Error: Could not read file')
        return elsamples, elmsgs



    
    
#%% Detect bad samples
    
def mark_bad_samples(etsamples):
    # adds columns for bad samples (out of monitor, pa==0) 
    # TODO: is or correct??
    
    # Gaze Position
    # is out of the range of the monitor
    # The monitor has a size of 1920 x 1080 pixels
    # Idea: logical indexing
    ix_outside_samples = (etsamples.gx < -500) | (etsamples.gx > 2420) | (etsamples.gy < -500) | (etsamples.gy > 1580)
    percentage_outside = np.mean(ix_outside_samples)*100
    print("Caution: %.2f%% samples got removed as the calculated gazeposition is outside the monitor"%(percentage_outside))
    
    if (percentage_outside > 0.4):
        raise NameError('More than 40% of the data got removed because the gaze is outside the monitor.') 
    
    marked_samples = pd.DataFrame()
    marked_samples['outside'] = ix_outside_samples
    
    
    # Sampling Frequency
    # check how many samples there are with a fs worse than 120 Hz
    tmp = pd.DataFrame()
    tmp['fs'] = etsamples.smpl_time.diff()
    ix_bad_freq = tmp.fs > (1./120.)
    percentage_bad_freq = np.mean(ix_bad_freq)*100
    print("Report: %.2f%% samples have a sampling frequency worse than 120 Hz"%(percentage_bad_freq))
    
    
    # Pupil Area
    # If pa is 0
    # ToDo check this
    etsamples.loc[etsamples['pa'] == 0,'zero_pa'] = True     
    
 

    return marked_samples


#%% Remove bad samples
    
def remove_bad_samples(marked_samples):
    # Input:      samples df that has coulmns that mark bad samples with 'True'
    # Output:     cleaned sample df where rows th
       
   # check if columns that mark bad samples exist
   assert('outside' in marked_samples)
   assert('is_blink' in marked_samples)
   assert('pa' in marked_samples)
    
   cleaned_samples = marked_samples[marked_samples['is_blink']==False]
   
   return cleaned_samples


#%% MAKE EPOCHS

def make_epochs(et,msgs,td=[-2,2]):
    # formally called match_data

    # Input:    et(DataFrame)      input data of the eyetracker (has column smpl_time)
    #           msgs(DataFrame)    already parsed input messages    e.g. 'GRID element 5 pos-x 123 ...' defining experimental events (has column msg_time)
    # Output:   df for each notification,
    #           find all samples that are in the range of +-td (default timediff 2 s)
    
    epoched_data = pd.DataFrame()
    
    for idx,msg in msgs.iterrows():
        print(idx)
        ix = ((et['smpl_time'] - msg['msg_time'])>td[0]) & ((et['smpl_time'] - msg['msg_time'])<td[1]) # ix is a boolean (0 / 1, false / true) (this way we find all samples +-td)
        if np.sum(ix) == 0:
            print('warning, no sample found for msg %i'%(idx))
            print(msg)
            continue
        tmp= et.loc[ix]
        tmp = tmp.assign(td=tmp.smpl_time-msg['msg_time'])
    
        msg_tmp = pd.concat([msg.to_frame()]*tmp.shape[0],axis=1).T
        msg_tmp.index = tmp.index
                
        tmp = pd.concat([tmp,msg_tmp],axis=1)
        epoched_data = epoched_data.append(tmp)
                 
    return(epoched_data)
    
 
#%% GET nice DATAFRAMES
 

# samples df 
def make_samples_df(etsamples):
    # function to check if all needed columns exist and get samples df
    assert('blink_id' in etsamples)
    assert('is_blink' in etsamples)
    assert('pa' in etsamples)
    
    if 'confidence' in etsamples:
        return etsamples.loc[:, ['smpl_time', 'gx', 'gy', 'confidence', 'pa', 'is_blink', 'blink_id', 'type']]
    
    elif 'pa_left' in etsamples.columns:
        return etsamples.loc[:, ['smpl_time', 'gx', 'gy', 'gx_vel', 'gy_vel', 'pa', 'is_blink', 'blink_id']]

    else:
        raise 'Error should not come here'

   
#%% 
# FULL df
# TODO
def make_full_df(etmsgs, etevents, condition):
    # Input:
    # Output:    
    full_df = pd.DataFrame()
    # search for start message of condition in **etmsgs**
    
    # search for first saccade / fixation / blink after msg_time in **etevents**
    
    return full_df

   
#%% HELPERS
    
def findFile(path,ftype):
    # finds file for el edf
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out)


 
        
