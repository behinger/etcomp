#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd

import os

from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
from functions.et_helper import findFile,gaze_to_pandas
import functions.et_parse as parse
import functions.make_df as df
try:
    import functions.pl_surface as pl_surface
except ImportError:
    print('Could not import pl_surface')
    



import logging
logger = logging.getLogger()



# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib


#%% PUPILLABS

def raw_pl_data(subject, datapath='/net/store/nbp/projects/etcomp/'):
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



def import_pl(subject, datapath='/net/store/nbp/projects/etcomp/', recalib=True, surfaceMap=True):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
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
        print('Original Data Samples:',len(original_pldata['gaze_positions']),'on surface:',len(gaze_on_srf))
        original_pldata['gaze_positions'] = gaze_on_srf
        

    # use pupilhelper func to make samples df (confidence, gx, gy, smpl_time, diameter)
    pldata = gaze_to_pandas(original_pldata['gaze_positions'])
    
    if surfaceMap:   
        pldata.gx = pldata.gx*(1920 - 2*(75+18))+(75+18) # minus white border of marker & marker
        pldata.gy = pldata.gy*(1080- 2*(75+18))+(75+18)
        print('Mapped Surface to ScreenSize 1920 & 1080 (minus markers)')
        del tracker
    # sort according to smpl_time
    pldata.sort_values('smpl_time',inplace=True)
    

    # get the nice samples df
    plsamples = df.make_samples_df(pldata) #
    

    # Get msgs df      
    # make a list of gridnotes that contain all notifications of original_pldata if they contain 'label'
    gridnotes = [note for note in original_pldata['notifications'] if 'label' in note.keys()]
    plmsgs = pd.DataFrame();
    for note in gridnotes:
        msg = parse.parse_message(note)
        if not msg.empty:
            plmsgs = plmsgs.append(msg, ignore_index=True)
    
    plevents = pd.DataFrame()
    plmsgs = fix_smallgrid_parser(plmsgs)
        
    return plsamples, plmsgs,plevents




  
#%% EYELINK

def import_el(subject, datapath='/net/store/nbp/projects/etcomp/'):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
    # Output:   Returns list of 2 el df (elsamples, elmsgs)

    assert(type(subject)==str)
    
    # Load edf
    filename = os.path.join(datapath,subject,'raw')
    
    # load and preprocess data from raw data files      
    # elsamples:  contains individual EL samples
    # elevents:   contains fixation and saccade definitions
    # elnotes:    contains notes (meta data) associated with each trial
    
    
    elsamples, elevents, elnotes = edf.pread(os.path.join(filename,findFile(filename,'.EDF')[0]), trial_marker=b'')
    if np.any(elsamples.time>1e13):
        logging.warning('Attention: Found sampling time above 1*e100. This is clearly wrong. Trying again,lets see whether we get an error (will check again later)')
        elsamples, elevents, elnotes = edf.pread(os.path.join(filename,findFile(filename,'.EDF')[0]), trial_marker=b'')
        
        
    
    
    # We also delete Samples with interpolated pupil responses. In one dataset these were ~800samples.
    print('Deleting %.4f%% due to interpolated pupil (online during eyelink recording)'%(100*np.mean(elsamples.errors ==8)))
    print('Deleting %.4f%% due to other errors in the import process'%(100*np.mean((elsamples.errors !=8) & (elsamples.errors!=0))))
    elsamples = elsamples.loc[elsamples.errors == 0]
    # We had issues with samples with negative time
    
    print('Deleting %.4f%% samples due to time<=0'%(100*np.mean(elsamples.time<=0)))
    elsamples = elsamples.loc[elsamples.time > 0]
    
    # Also at the end of the recording, we had time samples that were smaller than the first sample.
    # Note that this assumes the samples are correctly ordered and the last samples actually 
    # refer to artefacts. If you use %SYNCTIME% this might be problematic (don't know how nwilming's edfread incorporates synctime)
    print('Deleting %.4f%% samples due to time being less than the starting time'%(100*np.mean(elsamples.time <= elsamples.time[0])))
    elsamples = elsamples.loc[elsamples.time > elsamples.time[0]]
    
    # Convert to same units
    # change to seconds to be the same as pupil
    elsamples['smpl_time'] = elsamples['time'] / 1000 
    elnotes['msg_time']    = elnotes['trialid_time'] / 1000
    elnotes = elnotes.drop('trialid_time',axis=1)  
    elevents['start']      = elevents['start'] / 1000     
    elevents['end']        = elevents['end'] / 1000             
    
    if np.any(elsamples.smpl_time>1e10):
        raise Exception('Error, even after reloading the data once, found sampling time above 1*e100. This is clearly wrong. Investigate')

    # for horizontal gaze component
    # Idea: Logical indexing
    ix_left = elsamples.gx_left  != -32768 
    ix_right = elsamples.gx_right != -32768

    # take the pupil area pa of the recorded eye
    # set pa to NaN instead of 0  or -32768
    elsamples.loc[elsamples['pa_right'] < 1e-20,'pa_right'] = np.nan
    elsamples.loc[~ix_right,'pa_right'] = np.nan
    elsamples.loc[elsamples['pa_left'] < 1e-20,'pa_left'] = np.nan
    elsamples.loc[~ix_left,'pa_left'] = np.nan
    
    # add pa column that takes the value that is not NaN
    ix_left  = ~np.isnan(elsamples.pa_left)
    ix_right = ~np.isnan(elsamples.pa_right)
    
    # init with nan
    elsamples['pa'] = np.nan
    
    elsamples.loc[ix_left, 'pa'] = elsamples.pa_left[ix_left]
    elsamples.loc[ix_right,'pa'] = elsamples.pa_right[ix_right]
    
    
    # Determine which eye was recorded

    ix_left = elsamples.gx_left   != -32768 
    ix_right = elsamples.gx_right != -32768

    if (np.mean(ix_left | ix_right)<0.99):
        raise NameError('In more than 1 % neither left or right data')
        
    
    # for horizontal gaze component    
    elsamples.loc[ix_left,'gx']      = elsamples.gx_left[ix_left]
    elsamples.loc[ix_right,'gx']     = elsamples.gx_right[ix_right]

    # for horizontal gaze velocity component
    elsamples.loc[ix_left,'gx_vel']  = elsamples.gxvel_left[ix_left]
    elsamples.loc[ix_right,'gx_vel'] = elsamples.gxvel_right[ix_right]
    
    
    # for vertical gaze component
    ix_left = elsamples.gy_left   != -32768 
    ix_right = elsamples.gy_right != -32768
    
    elsamples.loc[ix_left,'gy']    = elsamples.gy_left[ix_left]
    elsamples.loc[ix_right,'gy']   = elsamples.gy_right[ix_right]
    
    # for vertical gaze velocity component
    elsamples.loc[ix_left,'gy_vel']  = elsamples.gyvel_left[ix_left]
    elsamples.loc[ix_right,'gy_vel'] = elsamples.gyvel_right[ix_right]
    
    
    # "select" relevant columns
    elsamples = df.make_samples_df(elsamples)
            
        
    # Parse EL msg
    elmsgs = elnotes.apply(parse.parse_message,axis=1)
    elmsgs = elmsgs.drop(elmsgs.index[elmsgs.isnull().all(1)])
    elmsgs = fix_smallgrid_parser(elmsgs)
    return elsamples, elmsgs, elevents
    



def fix_smallgrid_parser(etmsgs):
    replaceGrid = pd.Series([k for l in [13*['SMALLGRID_BEFORE'],13*['SMALLGRID_AFTER']]*6 for k in l])
    ix = etmsgs.query('grid_size==13').index
    if len(ix) is not  156:
        raise RuntimeError('we need to have 156 small grid msgs')

    replaceGrid.index = ix
    etmsgs.loc[ix,'condition'] = replaceGrid
    return(etmsgs)
    
    