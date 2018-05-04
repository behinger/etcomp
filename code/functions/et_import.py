#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
import math
import os,sys,inspect

from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import os
import functions.nbp_pupilhelper as nbp_pl
import functions.etcomp_parse as parse
#import functions.pl_surface as pl_surface

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

def preprocess_pl(subject, datapath='/net/store/nbp/projects/etcomp/pilot', recalib=False, surfaceMap = False):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
    #           recalib:
    #           surfaceMap:
    # Output:   Returns 2 dfs (plsamples and plmsgs)

    assert(type(subject)==str)

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
    
    plsamples = make_samples_df(pldata)


    # Get msgs df      
    # make a list of gridnotes that contain all notifications of original_pldata if they contain 'label'
    gridnotes = [note for note in original_pldata['notifications'] if 'label' in note.keys()]
    plmsgs = pd.DataFrame();
    for note in gridnotes:
        msg = parse.parse_message(note)
        if not msg.empty:
            plmsgs = plmsgs.append(msg, ignore_index=True)
    

    return plsamples, plmsgs

  
#%% EYELINK

def preprocess_el(subject, datapath='/net/store/nbp/projects/etcomp/pilot'):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
    # Output:   Returns list of 2 el df (elsamples, elmsgs)
    
    # Load edf
    filename = os.path.join(datapath,subject,'raw')
    
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

    # take the pupil area pa of the recorded eye
    # set pa to NaN instead of 0  or -32768
    elsamples.loc[elsamples['pa_right'] == 0,'pa_right'] = np.nan
    elsamples.loc[elsamples['pa_right'] == -32768,'pa_right'] = np.nan
    elsamples.loc[elsamples['pa_left'] == 0,'pa_left'] = np.nan
    elsamples.loc[elsamples['pa_left'] == -32768,'pa_left'] = np.nan
    
    # add pa column that takes the value that is not NaN
    # TODO
    ix_left = elsamples.pa_left  != np.nan 
    ix_right = elsamples.pa_right != np.nan
    
    elsamples.loc[ix_left,'pa'] = elsamples.pa_left[ix_left]
    elsamples.loc[ix_right,'pa'] = elsamples.pa_right[ix_right]
    
    
    # Determine which eye was recorded

    # for horizontal gaze component
    # Idea: Logical indexing
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
            
    
    # Parse EL msg
    elmsgs = elnotes.apply(parse.parse_message,axis=1)
    elmsgs = elmsgs.drop(elmsgs.index[elmsgs.isnull().all(1)])

        
    return make_samples_df(elsamples), elmsgs
    
#%% Detect bad samples
    
def remove_bad_samples(etsamples):
    # Idea: logical indexing
    # TODO: is or correct??
    ix_badsamples = etsamples.index[(etsamples.gx < -500) | (etsamples.gx > 2420) | (etsamples.gy < -500) | (etsamples.gy > 1580)]
    number_bad_samples = np.mean(ix_badsamples)
    
    print("Caution: {} samples got removed as the calculated gazeposition is outside the monitor".format(number_bad_samples))
    
    if (number_bad_samples > 0.2):
        raise NameError('More than 20% of the data got removed')

    cleaned_samples = etsamples.drop(ix_badsamples)
    
    
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
    # function to get samples df
    if 'confidence' in etsamples:
        return etsamples.loc[:, ['smpl_time', 'gx', 'gy', 'confidence', 'pa']]
    
    # this should be the pupil area, but do the numbers make sense??
    # TODO add diameter
    elif 'pa_left' in etsamples.columns:
        return etsamples.loc[:, ['smpl_time', 'gx', 'gy', 'gx_vel', 'gy_vel', 'pa_left', 'pa_right', 'pa']]

    else:
        raise 'Error should not come here'


    
# events df
# TODO
def make_events(etsamples):
    # is this conceptually correct?
    etevents = make_events(etsamples)
    # return etevents
    pass



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


 
        
