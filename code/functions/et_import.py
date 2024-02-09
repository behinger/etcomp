#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import pandas as pd

import os
import logging

from functions.et_helper import findFile,gaze_to_pandas
import functions.et_parse as parse
import functions.et_make_df as make_df
import functions.et_helper as  helper

import imp # for edfread reload


import scipy
import scipy.stats

#%% PUPILLABS
def pl_fix_timelag(pl):
    #fixes the pupillabs latency lag (which can be super large!!)

    t_cam = np.asarray([p['recent_frame_timestamp'] for p in pl['notifications'] if p['subject']=='trigger'])# camera time
    t_msg = np.asarray([p['timestamp'] for p in pl['notifications'] if p['subject']=='trigger']) # msg time
    
    #slope, intercept, r_value, p_value, std_err  = scipy.stats.linregress(t_msg,t_cam) # predict camera time based on msg time
    slope,intercept,low,high = scipy.stats.theilslopes(t_cam,t_msg)
    logger = logging.getLogger(__name__)
    logger.warning("fixing lag (at t=0) of :%.2fms, slope of %.7f (in a perfect world this is 0ms & 1.0)"%(intercept*1000,slope))
    # fill it back in
    # gonna do it with a for-loop because other stuff is too voodo or not readable for me
    
    
    # Use this code (and change t_cam and t_msg above) if you want everything in computer time timestamps
    #for ix,m in enumerate(pl['gaze_positions']):
    #    pl['gaze_positions'][ix]['timestamp'] = pl['gaze_positions'][ix]['timestamp']  * slope + intercept   
    #    for ix2,m2 in enumerate(pl['gaze_positions'][ix]['pupil_positions']):
    #            pl['gaze_positions'][ix]['pupil_positions']['timestamp'] = pl['gaze_positions'][ix]['pupil_positions']['timestamp']  * slope + intercept
    #for ix,m in enumerate(pl['gaze_positions']):
    #     pl['pupil_positions'][ix]['timestamp'] = pl['pupil_positions'][ix]['timestamp']  * slope + intercept# + 0.045 # the 45ms  are the pupillabs defined delay between camera image & timestamp3   
        
    # this code is to get notifications into sample time stamp. But for now we 
    for ix,m in enumerate(pl['notifications']):
        pl['notifications'][ix]['timestamp'] = pl['notifications'][ix]['timestamp']  * slope + intercept + 0.045 # the 45ms  are the pupillabs defined delay between camera image & timestamp3
        
    return(pl)

def raw_pl_data(subject='',datapath='/net/store/nbp/projects/etcomp/',postfix='raw'):
    # Input:    subjectname, datapath
    # Output:   Returns pupillabs dictionary
    from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
    
    if subject == '':
        filename = datapath
    else:
        filename = os.path.join(datapath,subject,postfix)
    print(os.path.join(filename,'pupil_data'))
    # with dict_keys(['notifications', 'pupil_positions', 'gaze_positions'])
    # where each value is a list that contains a dictionary
    original_pldata = pl_file_methods.load_object(os.path.join(filename,'pupil_data'))
    #original_pldata = pl_file_methods.Incremental_Legacy_Pupil_Data_Loader(os.path.join(filename,'pupil_data'))
    # 'notification'
    # dict_keys(['record', 'subject', 'timestamp', 'label', 'duration'])
    
    # 'pupil_positions'
    # dict_keys(['diameter', 'confidence', 'method', 'norm_pos', 'timestamp', 'id', 'topic', 'ellipse'])
    
    # 'gaze_positions'
    # dict_keys(['base_data', 'timestamp', 'topic', 'confidence', 'norm_pos'])
        # where 'base_data' has a dict within a list 
        # dict_keys(['diameter', 'confidence', 'method', 'norm_pos', 'timestamp', 'id', 'topic', 'ellipse'])
        # where 'normpos' is a list (with horizon. and vert. component)
    
    # Fix the (possible) timelag of pupillabs camera vs. computer time
    
    
    
    return original_pldata


def import_pl(subject='', datapath='/net/store/nbp/projects/etcomp/', recalib=True, surfaceMap=True,parsemsg=True,fixTimeLag=True,px2deg=True,pupildetect=None,
             pupildetect_options=None):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
    #           surfaceMap:
    # Output:   Returns 2 dfs (plsamples and plmsgs)
    
    # get a logger
    logger = logging.getLogger(__name__)
    if pupildetect:
        # has to be imported first
        import av
        import ctypes
        ctypes.cdll.LoadLibrary('/net/store/nbp/users/behinger/projects/etcomp/local/build/build_ceres_working/lib/libceres.so.2')

    
    if surfaceMap:
        # has to be imported before nbp recalib
        try:
            import functions.pl_surface as pl_surface
        except ImportError:
            raise('Custom Error:Could not import pl_surface')


    assert(type(subject)==str)
    
    # Get samples df
    # (is still a dictionary here)
    original_pldata = raw_pl_data(subject=subject, datapath=datapath)
        
    if pupildetect is not None: # can be 2d or 3d
        from functions.nbp_pupildetect import  nbp_pupildetect
        if subject == '':
            filename = datapath
        else:
            filename = os.path.join(datapath,subject,'raw')
   
        pupil_positions_0= nbp_pupildetect(detector_type = pupildetect, eye_id = 0,folder=filename,pupildetect_options=pupildetect_options)
        pupil_positions_1= nbp_pupildetect(detector_type = pupildetect, eye_id = 1,folder=filename,pupildetect_options=pupildetect_options)
        pupil_positions = pupil_positions_0 + pupil_positions_1
        original_pldata['pupil_positions'] = pupil_positions
        recalib=True
        
    # recalibrate data
    if recalib:
        from functions import nbp_recalib
        if pupildetect is not None:
            original_pldata['gaze_positions'] = nbp_recalib.nbp_recalib(original_pldata,calibration_mode=pupildetect)
        original_pldata['gaze_positions'] = nbp_recalib.nbp_recalib(original_pldata)
    # Fix timing 
    # Pupillabs cameras ,have their own timestamps & clock. The msgs are clocked via computertime. Sometimes computertime&cameratime show drift (~40% of cases).
    # We fix this here
    if fixTimeLag:
        original_pldata = pl_fix_timelag(original_pldata)  
    
    if surfaceMap:

        folder= os.path.join(datapath,subject,'raw')
        tracker = pl_surface.map_surface(folder)   
        gaze_on_srf  = pl_surface.surface_map_data(tracker,original_pldata['gaze_positions'])
        logger.warning('Original Data Samples: %s on surface: %s',len(original_pldata['gaze_positions']),len(gaze_on_srf))
        original_pldata['gaze_positions'] = gaze_on_srf
        
    
    # use pupilhelper func to make samples df (confidence, gx, gy, smpl_time, diameter)
    pldata = gaze_to_pandas(original_pldata['gaze_positions'])
    
    
    
    if surfaceMap:   
        pldata.gx = pldata.gx*(1920 - 2*(75+18))+(75+18) # minus white border of marker & marker
        pldata.gy = pldata.gy*(1080- 2*(75+18))+(75+18)
        logger.debug('Mapped Surface to ScreenSize 1920 & 1080 (minus markers)')
        del tracker

    # sort according to smpl_time
    pldata.sort_values('smpl_time',inplace=True)
    

    # get the nice samples df
    plsamples = make_df.make_samples_df(pldata,px2deg=px2deg) #
    
    
    if parsemsg:
        # Get msgs df      
        # make a list of gridnotes that contain all notifications of original_pldata if they contain 'label'
        gridnotes = [note for note in original_pldata['notifications'] if 'label' in note.keys()]
        plmsgs = pd.DataFrame();
        for note in gridnotes:
            msg = parse.parse_message(note)
            if not msg.empty:
                plmsgs = plmsgs.append(msg, ignore_index=True)

        
        plmsgs = fix_smallgrid_parser(plmsgs)
    else:
        plmsgs = original_pldata['notifications']
        
    plevents = pd.DataFrame()
    return plsamples, plmsgs,plevents


#%% TRACKPIXX



  
#%% EYELINK

def drop_eye(samples, events, subject, participantinfo):
    """
    Filters data for the dominant eye from a dataframe (e.g. a sample report) based on a participant reference dataframe.
    
    Parameters:
        samples (pd.DataFrame): The samples DataFrame from which COLUMNS will be removed.
        events (pd.DataFrame): The events DataFrame from which ROWS will be removed.
        subject (str): A string containing the subject ID.
        participantinfo (pd.DataFrame): The DataFrame containing the dominant eye information ('Rechts' for right, 'Links' for left).
    Returns:
        selection (pd.DataFrame): The modified DataFrame where non-dominant eye columns are removed and the remaining gaze-related columns are renamed.
    """
    logger = logging.getLogger(__name__)

    eye = participantinfo.loc[participantinfo['ID'] == subject, 'DominantEye'].iloc[0]
    logger.warning('Selecting the eye: %s', eye)
    if eye == 'Rechts':
        # Samples right
        drop_columns = samples.filter(like='_left', axis=1)
        elsamples = samples.drop(columns = drop_columns)
        elsamples.rename(columns={'gx_right': 'gx', 
                                  'gy_right': 'gy',
                                  'gxvel_right': 'gxvel',
                                  'gyvel_right': 'gyvel',
                                  'pa_right': 'pa',
                                  'px_right': 'px',
                                  'py_right': 'py',
                                  'hx_right': 'hx',
                                  'hy_right': 'hy',
                                  'hxvel_right': 'hxvel',
                                  'hyvel_right': 'hyvel',
                                  'rxvel_right': 'rxvel',
                                  'ryvel_right': 'ryvel'}, 
                         inplace=True)
        if 'b_right' not in samples.columns:
            logger.warning("DataFrame does not have the 'b_right' column.")
        else:
            elsamples.rename(columns={'b_right': 'blink'}, inplace=True)

        # Events right
        elevents = events.loc[events['eye'] == 1]

    elif eye == 'Links':
        # Samples left
        drop_columns = samples.filter(like='_right', axis=1)
        elsamples = samples.drop(columns = drop_columns)
        elsamples.rename(columns={'gx_left': 'gx', 
                                  'gy_left': 'gy',
                                  'gxvel_left': 'gxvel',
                                  'gyvel_left': 'gyvel',
                                  'pa_left': 'pa',
                                  'px_left': 'px',
                                  'py_left': 'py',
                                  'hx_left': 'hx',
                                  'hy_left': 'hy',
                                  'hxvel_left': 'hxvel',
                                  'hyvel_left': 'hyvel',
                                  'rxvel_left': 'rxvel',
                                  'ryvel_left': 'ryvel'}, 
                         inplace=True)
        if 'b_left' not in samples.columns:
            logger.warning("DataFrame does not have the 'b_left' column.")
        else:
            elsamples.rename(columns={'b_left': 'blink'}, inplace=True)

        # Events left
        elevents = events.loc[events['eye'] == 0]
    
    else:
        logger.error("Unknown eye '%s' for participant ID: %s", eye, subject)
        
    return elsamples, elevents

def raw_el_data(subject, datapath='/net/store/nbp/projects/etcomp/'):
    # Input:    subjectname, datapath
    # Output:   Returns pupillabs dictionary
    filename = os.path.join(datapath,subject,'raw')
    import  edfread # parses SR research EDF data files into pandas df

    elsamples, elevents, elnotes = edfread.read_edf(os.path.join(filename,findFile(filename,'.EDF')[0]))#, trial_marker=b'')
    
    return (elsamples,elevents,elnotes)
    
    
def import_el(subject, participantinfo, datapath='/net/store/nbp/projects/etcomp/'):
    # Input:    subject:         (str) name
    #           datapath:        (str) location where data is stored
    # Output:   Returns list of 3 el df (elsamples, elmsgs, elevents)

    assert(type(subject)==str)
    
    # get a logger
    logger = logging.getLogger(__name__)
     
    
    # Load edf
    
    # load and preprocess data from raw data files      
    # elsamples:  contains individual EL samples
    # elevents:   contains fixation and saccade definitions
    # elnotes:    contains notes (meta data) associated with each trial
    elsamples,elevents,elnotes = raw_el_data(subject,datapath)
    
    # TODO understand and fix this
    count = 0
    while np.any(elsamples.time>1e10) and count < 40:
        from edfread import edf # parses SR research EDF data files into pandas df
        imp.reload(edf)
        count = count + 1
        # logger.error(elsamples.time[elsamples.time>1e10])
        logger.error('Attention: Found sampling time above 1*e100. Clearly wrong! Trying again (check again later)')
        elsamples, elevents, elnotes = raw_el_data(subject,datapath)
    
    if elsamples.iloc[0].time == elsamples.iloc[1].time:
        logger.warning('detected 2000Hz recording, adding 0.5 to every second sample (following SR-Support)')
        elsamples.loc[::2, 'time'] = elsamples.loc[::2, 'time'] + 0.5
    
    # We also delete Samples with interpolated pupil responses. In one dataset these were ~800samples.
    logger.warning('Deleting %.4f%% due to interpolated pupil (online during eyelink recording)'%(100*np.mean(elsamples.errors ==8)))
    logger.warning('Deleting %.4f%% due to other errors in the import process'%(100*np.mean((elsamples.errors !=8) & (elsamples.errors!=0))))
    elsamples = elsamples.loc[elsamples.errors == 0]
    
    # We had issues with samples with negative time
    logger.warning('Deleting %.4f%% samples due to time<=0'%(100*np.mean(elsamples.time<=0)))
    elsamples = elsamples.loc[elsamples.time > 0]
    
    # Also at the end of the recording, we had time samples that were smaller than the first sample.
    # Note that this assumes the samples are correctly ordered and the last samples actually 
    # refer to artefacts. If you use %SYNCTIME% this might be problematic (don't know how nwilming's edfread incorporates synctime)
    logger.warning('Deleting %.4f%% samples due to time being less than the starting time'%(100*np.mean(elsamples.time <= elsamples.time[0])))
    elsamples = elsamples.loc[elsamples.time > elsamples.time[0]]
    elsamples = elsamples.reset_index()
    # Convert to same units
    # change to seconds to be the same as pupil
    elsamples['smpl_time'] = elsamples['time'] / 1000 
    elnotes['msg_time']    = elnotes['time'] / 1000
    #logger.warning(type(elnotes))
    elnotes = elnotes.drop('time',axis=1)  
    elevents['start']      = elevents['start'] / 1000     
    elevents['end']        = elevents['end'] / 1000             
    
    # TODO solve this!
    if np.any(elsamples.smpl_time>1e10):
        logger.error(elsamples.smpl_time[elsamples.smpl_time>1e10])
        logger.error('Error, even after reloading the data once, found sampling time above 1*e100. This is clearly wrong. Investigate')
        raise Exception('Error, even after reloading the data once, found sampling time above 1*e100. This is clearly wrong. Investigate')

    # Determine which eye was recorded
    elsamples, elevents = drop_eye(elsamples, elevents, subject, participantinfo)

    # for horizontal gaze component
    # Idea: Logical indexing
    ix = elsamples.gx != -32768

    # take the pupil area pa of the recorded eye
    # set pa to NaN instead of 0  or -32768
    elsamples.loc[elsamples['pa'] < 1e-20,'pa'] = np.nan
    elsamples.loc[~ix,'pa'] = np.nan
    ix  = ~np.isnan(elsamples.pa)
    elsamples.loc[ix,'pa'] = elsamples.pa[ix]

    # for horizontal gaze component    
    ix = elsamples.gx   != -32768 
    elsamples.loc[ix,'gx']      = elsamples.gx[ix]
    # for horizontal gaze velocity component
    elsamples.loc[ix,'gx_vel']  = elsamples.gxvel[ix]
       
    # for vertical gaze component
    ix = elsamples.gy   != -32768 
    elsamples.loc[ix,'gy']    = elsamples.gy[ix]
    # for vertical gaze velocity component
    elsamples.loc[ix,'gy_vel']  = elsamples.gyvel[ix]
    
    # Make (0,0) the point bottom left
    elsamples['gy'] = 1080 - elsamples['gy']
    
    # "select" relevant columns
    elsamples = make_df.make_samples_df(elsamples)
                
    # Parse EL msg
    elmsgs = elnotes.apply(parse.parse_message,axis=1)
    #logger.warning(elmsgs)
    
    elmsgs = elmsgs.drop(elmsgs.index[elmsgs.isnull().all(1)])
    #elmsgs = fix_smallgrid_parser(elmsgs)
    
    return elsamples, elmsgs, elevents
    



def fix_smallgrid_parser(etmsgs):
    # This fixes the missing separation between smallgrid before and small grid after. During experimental sending both were named identical.
    replaceGrid = pd.Series([k for l in [13*['SMALLGRID_BEFORE'],13*['SMALLGRID_AFTER']]*6 for k in l])
    ix = etmsgs.query('grid_size==13').index
    if len(ix) is not  156:
        raise RuntimeError('we need to have 156 small grid msgs')

    replaceGrid.index = ix
    etmsgs.loc[ix,'condition'] = replaceGrid
    
    # this here fixes that all buttonpresses and stop messages etc. were send as GRID and not SMALLGG 
    for blockid in etmsgs.block.dropna().unique():
        if blockid == 0:
            continue
        tmp = etmsgs.query('block==@blockid')
        t_before_start = tmp.query('condition=="DILATION"& exp_event=="stop"').msg_time.values
        t_before_end   = tmp.query('condition=="SHAKE"   & exp_event=="stop"').msg_time.values
        t_after_start  = tmp.query('condition=="SHAKE"   & exp_event=="stop"').msg_time.values
        t_after_end    =tmp.iloc[-1].msg_time

        ix = tmp.query('condition=="GRID"&msg_time>@t_before_start & msg_time<=@t_before_end').index
        etmsgs.loc[ix,'condition'] = 'SMALLGRID_BEFORE'
        
        ix = tmp.query('condition=="GRID"&msg_time>@t_after_start  & msg_time<=@t_after_end').index
        etmsgs.loc[ix,'condition'] = 'SMALLGRID_AFTER'
        
    return(etmsgs)
    
    