#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import edfread # parses SR research EDF data files into pandas df
import imp # for edfread reload
import logging
import os
import numpy as np
import pandas as pd
import re
from scipy import io as sio

from functions.et_helper import findFile
import functions.et_parse as parse
import functions.et_make_df as make_df
import functions.et_helper as  helper


#%% TRACKPIXX

def read_mat(subject, datapath='./data'):
    """
    Read raw MAT data files as exported by Matlab for TrackPixx

    Parameters:
        subject (str): Participant ID
        datapath (str): Data location
    Returns: 
        combined_df (pd.DataFrame): A DataFrame with added information about the block and participant
    """
    logger = logging.getLogger(__name__)
    directory = os.path.join(datapath, subject, 'raw')  
    tpxsamples = []
    
    try:
        # Get a list of filenames and sort them based on the block number
        filenames = [filename for filename in os.listdir(directory) if filename.endswith("tpx.mat")]
        filenames.sort(key=lambda x: int(re.search(r'block-(\d+)_tpx.mat', x).group(1)))

        for filename in filenames:
            filepath = os.path.join(directory, filename)
            logger.warning('Reading file %s', filename)
            mat = sio.loadmat(filepath)
            data = mat['bufferData']
            cols = mat['varnames'][0].split(',')
            df = pd.DataFrame(data=data, columns=cols)
                
            df['block'] = int(re.search(r'block-(\d+)_tpx.mat', filename).group(1))
            df['ID'] = filename[0:7]
               
            tpxsamples.append(df)
    
        if not tpxsamples:
            raise ValueError("No 'tpx.mat' files found in the directory.")
    
        combined_df = pd.concat(tpxsamples, ignore_index=True)
    
        return combined_df
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def load_messages(subject, datapath='./data', pattern=r'^sub-\d{3}_events.csv$'):
    """
    Import the message report for TrackPixx.

    Parameters:
        subject (str): Participant ID
        datapath (str): Data location
        pattern (str): A regular expression for parsing participant IDs
    Returns: 
        combined_msgs (pd.DataFrame): A DataFrame with all messages
    """
    logger = logging.getLogger(__name__)
    all_msgs = []
    file_pattern = re.compile(pattern)
    directory = os.path.join(datapath, subject, 'raw')
        
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if file_pattern.match(filename):
                file_path = os.path.join(root, filename)
                logger.warning('Reading file %s', filename)
                df = pd.read_csv(file_path)             
                df['ID'] = subject
                all_msgs.append(df)

    combined_msgs = pd.concat(all_msgs, ignore_index=True)

    return combined_msgs

    all_msgs = []
    file_pattern = re.compile(pattern)

    for root, dirs, files in os.walk(directory):
        if excludeID is not None and os.path.basename(root) in excludeID:
                continue
        
        for filename in files:
            if file_pattern.match(filename):
                file_path = os.path.join(root, filename)
                print('Reading file', filename)
                df = pd.read_csv(file_path)             
                df['ID'] = filename[0:7]
                
                all_msgs.append(df)

    combined_msgs = pd.concat(all_msgs, ignore_index=True)

    return combined_msgs

def load_wordbounds(directory='./data'):
    """
    This function reads and processes CSV files with word bounding box coordinates 
    for the reading task.

    Parameters:
        directory (str): The path to the directory containing the CSV files.
    Returns:
        bounds (pd.DataFrame): A DataFrame containing word boundary data.
    """
    for root, _, files in os.walk(directory):
        for filename in files:
            if 'wordbounds' in filename and filename.endswith('.csv'):
                print(f"Processing file: {filename}")
                file_path = os.path.join(root, filename)
                bounds = pd.read_csv(file_path, names=['top_left_x', 'top_left_y', 'bottom_right_x', 'bottom_right_y'])
                bounds['block'] = re.findall(r"block-(\d+)_task", filename)[0]
                bounds['ID'] = root[-11:-4]
                bounds['word'] = range(1, len(bounds) + 1)
                bounds.sort_values(by=['ID', 'block', 'word'], inplace=True)

    return bounds
  
def import_tpx(subject, participant_info, datapath='./data'):
    logger = logging.getLogger(__name__)
    logger.warning(datapath)
    tpxsamples = read_mat(subject, datapath)
    tpxsamples.rename(columns={'TimeTag': 'smpl_time', 
                               'RightEyeX': 'gx_right', 
                               'LeftEyeX': 'gx_left',
                               'RightEyeY': 'gy_right', 
                               'LeftEyeY': 'gy_left', 
                               'RightBlink' : 'b_right', 
                               'LeftBlink' : 'b_left', 
                               'RightPupilDiameter': 'pa_right', 
                               'LeftPupilDiameter' : 'pa_left'}, inplace=True)
    # We had issues with samples with negative time
    logger.warning('Deleting %.4f%% samples due to time<=0'%(100*np.mean(tpxsamples.smpl_time<=0)))
    tpxsamples = tpxsamples.loc[tpxsamples.smpl_time > 0]
    logger.warning('Deleting %.4f%% samples due to time being less than the starting time'%(100*np.mean(tpxsamples.smpl_time <= tpxsamples.smpl_time[0])))
    tpxsamples = tpxsamples.loc[tpxsamples.smpl_time > tpxsamples.smpl_time[0]]
    tpxsamples = tpxsamples.reset_index()
    if np.any(tpxsamples.smpl_time>1e10):
        logger.error(tpxsamples.smpl_time[tpxsamples.smpl_time>1e10])
        logger.error('Error, even after reloading the data once, found sampling time above 1*e100. This is clearly wrong. Investigate')
        raise Exception('Error, even after reloading the data once, found sampling time above 1*e100. This is clearly wrong. Investigate')
    
    # Determine which eye was recorded
    tpxsamples, tpxevents = drop_eye(subject, participant_info, tpxsamples)
    
    # for horizontal gaze component
    # Idea: Logical indexing
    ix = tpxsamples.gx != -32768
    # take the pupil area pa of the recorded eye
    # set pa to NaN instead of 0  or -32768
    tpxsamples.loc[tpxsamples['pa'] < 1e-20,'pa'] = np.nan
    tpxsamples.loc[~ix,'pa'] = np.nan
    ix  = ~np.isnan(tpxsamples.pa)
    tpxsamples.loc[ix,'pa'] = tpxsamples.pa[ix]
    # for horizontal gaze component    
    ix = tpxsamples.gx   != -32768 
    tpxsamples.loc[ix,'gx']      = tpxsamples.gx[ix]
    # FIXME there is no velocity information for TrackPixx
    # for vertical gaze component
    ix = tpxsamples.gy   != -32768 
    tpxsamples.loc[ix,'gy']    = tpxsamples.gy[ix]
    # FIXME there is no velocity information for TrackPixx
    # Make (0,0) the point bottom left
    tpxsamples['gy'] = 1080 - tpxsamples['gy']
    # "select" relevant columns
    tpxsamples = make_df.make_samples_df(tpxsamples)

    tpxmsgs = load_messages(datapath) 
    tpxmsgs = tpxmsgs.apply(parse.parse_message,axis=1)
    tpxmsgs = tpxmsgs.drop(tpxmsgs.index[tpxmsgs.isnull().all(1)])
    
    return tpxsamples, tpxmsgs, pd.DataFrame() #FIXME why not return tpxevents? it's empty anyway

#%% EYELINK

def raw_el_data(subject, datapath='/net/store/nbp/projects/etcomp/'):
    # Input:    subjectname, datapath
    # Output:   Returns pupillabs dictionary
    filename = os.path.join(datapath,subject,'raw')

    elsamples, elevents, elnotes = edfread.read_edf(os.path.join(filename,findFile(filename,'.EDF')[0]))#, trial_marker=b'')
    
    return (elsamples,elevents,elnotes)
    
    
def import_el(subject, participant_info, datapath='/net/store/nbp/projects/etcomp/'):
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
    #logger.warning('Deleting %.4f%% due to interpolated pupil (online during eyelink recording)'%(100*np.mean(elsamples.errors ==8)))
    logger.warning('Marking as NaN %.4f%% due to other errors (e.g. lost eye / target)'%(100*np.mean((elsamples.errors!=0))))
    
    #elsamples = elsamples.loc[elsamples.errors == 0]
    elsamples.loc[elsamples.errors != 0,["gx_left","gy_left","gx_right","gx_left"]] = np.NaN
    
    # We had issues with samples with negative time
    logger.warning('Deleting %.4f%% samples due to time<=0'%(100*np.mean(elsamples.time<=0)))
    elsamples = elsamples.loc[elsamples.time > 0]
    
    # Also at the end of the recording, we had time samples that were smaller than the first sample.
    # Note that this assumes the samples are correctly ordered and the last samples actually 
    # refer to artefacts. If you use %SYNCTIME% this might be problematic (don't know how nwilming's edfread incorporates synctime)
    logger.warning('Deleting %.4f%% samples due to time being less than the starting time'%(100*np.mean(elsamples.time <= elsamples.time[0])))
    elsamples = elsamples.loc[elsamples.time > elsamples.time[0]]
    elsamples.reset_index(inplace=True)
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
    elsamples, elevents = drop_eye(subject, participant_info, elsamples, elevents)

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
    elsamples.loc[elsamples.gy < -900000,'gy'] = np.nan # no idea why this is necessary... should be NaN anyway
    # "select" relevant columns
    elsamples = make_df.make_samples_df(elsamples)
                
    # Parse EL msg
    elmsgs = elnotes.apply(parse.parse_message,axis=1)
    #logger.warning(elmsgs)
    
    elmsgs = elmsgs.drop(elmsgs.index[elmsgs.isnull().all(1)])
    #elmsgs = fix_smallgrid_parser(elmsgs)
    
    return elsamples, elmsgs, elevents
    


# FIXME do we still need this function? If so, it needs to be adjusted to TPX.
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
    
######################################################################
#                                                                    #
#  FUNCTIONS THAT PROBABLY NEED TO BE MOVED ELSEWHERE                #
#                                                                    #
######################################################################

def drop_eye(subject, participant_info,samples, events=None):
    """
    Filters data for the dominant eye from a dataframe (e.g. a sample report) based on a participant reference dataframe.
    
    Parameters:
        samples (pd.DataFrame): The samples DataFrame from which COLUMNS will be removed.
        events (pd.DataFrame): An optional events DataFrame from which ROWS will be removed.
        subject (str): A string containing the subject ID.
        participant_info (pd.DataFrame): The DataFrame containing the dominant eye information ('Rechts' for right, 'Links' for left).
    Returns:
        samples (pd.DataFrame): The modified DataFrame where non-dominant eye columns are removed and the remaining gaze-related columns are renamed.

    """
    logger = logging.getLogger(__name__)

    eye = participant_info.loc[participant_info['ID'] == subject, 'DominantEye'].iloc[0]
    logger.warning('Selecting the eye: %s', eye)
    if eye == 'Rechts':
        # Samples right
        drop_columns = samples.filter(like='_left', axis=1)
        samples = samples.drop(columns = drop_columns)
        samples.rename(columns={'gx_right': 'gx', 
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
            samples.rename(columns={'b_right': 'blink'}, inplace=True)

        # Events right
        if events is not None:
            events = events.loc[events['eye'] == 1]

    elif eye == 'Links':
        # Samples left
        drop_columns = samples.filter(like='_right', axis=1)
        samples = samples.drop(columns = drop_columns)
        samples.rename(columns={'gx_left': 'gx', 
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
            samples.rename(columns={'b_left': 'blink'}, inplace=True)

        # Events left
        if events is not None:
            events = events.loc[events['eye'] == 0]
    
    else:
        logger.error("Unknown eye '%s' for participant ID: %s", eye, subject)
        
    return samples, events


def make_lines(df, column_name='top_left_y'):
    """
    This function adds line information for the reading task. 
    The text read in this task was split into lines of up to 11 lines per display.

    Parameters:
        df (pd.DataFrame): The DataFrame to be processed.
        column_name (str): The name of the column containing values to be used for grouping.
    Returns:
        new_df (pd.DataFrame): A DataFrame with a new 'group' column containing group numbers.
    """
    lines = {
        1: (100, 105),
        2: (187, 192),
        3: (274, 286),
        4: (361, 366),
        5: (448, 453),
        6: (535, 540),
        7: (622, 627),
        8: (707, 714),
        9: (796, 801),
        10: (883, 888),
        11: (970, 975)
    }
    new_df = df.copy()
    new_df['line'] = None
    for group_num, value_range in lines.items():
        new_df.loc[new_df[column_name].between(value_range[0], value_range[1]), 'line'] = group_num
    return new_df


def load_files(directory, datatype):
    """
    Load and merge CSV files from multiple subdirectories into one pandas DataFrame.
    This is currently only used for loading participant information.

    Parameters:
        directory (str): Path to the main directory containing subdirectories with CSV files.
        eyetracker (str): Output of which eyetracker (el or tp)
        datatype (str): Type of CSV file (samples, msgs, or events)
    Returns:
        all_data (pd.DataFrame): Merged DataFrame containing data from all CSV files.
    """
    all_data = pd.DataFrame()

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(datatype+'.csv'):
                file_path = os.path.join(root, file)
                if datatype == "participant_info": 
                    data = pd.read_csv(file_path, sep=';')
                else: 
                    data = pd.read_csv(file_path, sep=',')
                print("Processing",file_path)
                all_data = pd.concat([all_data, data])

    return all_data