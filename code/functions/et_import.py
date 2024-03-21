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

from functions.et_helper import check_directory, drop_eye, findFile, regress_eyetracker
import functions.et_parse as parse
import functions.et_make_df as make_df

#%% TRACKPIXX

def read_mat(datapath='./data'):
    """
    Read raw MAT data files as exported by Matlab for TrackPixx

    Parameters:
        datapath (str): Data location
    Returns: 
        combined_df (pd.DataFrame): A DataFrame with added information about the block and participant
    """
    logger = logging.getLogger(__name__)
    tpxsamples = []
    
    try:
        # Get a list of filenames and sort them based on the block number
        filenames = [filename for filename in os.listdir(datapath) if filename.endswith("tpx.mat")]
        filenames.sort(key=lambda x: int(re.search(r'block-(\d+)_tpx.mat', x).group(1)))

        for filename in filenames:
            filepath = os.path.join(datapath, filename)
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

    try:
        check_directory(datapath)
    except FileNotFoundError as error:
        logger.warning("Directory not found. Error: %s", error)

    for root, dirs, files in os.walk(datapath):
        for filename in files:
            if file_pattern.match(filename):
                file_path = os.path.join(root, filename)
                df = pd.read_csv(file_path)             
                df['ID'] = subject
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


def import_tpx(subject, participant_info, datapath='/data/'):
    """
    This function imports TrackPixx eyetracking data for a specific subject from the specified 'datapath'.
    It first reads samples data from a .mat file using the `read_mat()` function. It then preprocesses the samples
    data, handling issues such as negative time values, sampling time above 1*e100, determining which eye was
    recorded, and setting pupil area and gaze components appropriately. It also reads and parses messages data
    using the `load_messages()` function.

    Parameters:
        subject (str): The subject ID.
        participant_info (pd.DataFrame): DataFrame containing participant information.
        datapath (str, optional): The directory path where the eyetracking data is located.

    Returns: A tuple containing three elements:
        tpxsamples (pandas.DataFrame): DataFrame containing samples report data.
        tpxmsgs (pandas.DataFrame): DataFrame containing messages data.
        tpxevents (pandas.DataFrame): DataFrame containing events data.
    """

    logger = logging.getLogger(__name__)

    try:
        check_directory(datapath)
    except FileNotFoundError as error:
        logger.warning("Directory not found. Error: %s", error)

    tpxsamples = read_mat(datapath)
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

    tpxmsgs = load_messages(subject, datapath) 
    tpxmsgs = tpxmsgs.apply(parse.parse_message,axis=1)
    tpxmsgs = tpxmsgs.drop(tpxmsgs.index[tpxmsgs.isnull().all(1)])
    
    return tpxsamples, tpxmsgs, tpxevents

#%% EYELINK

def raw_el_data(datapath='/data/'):
    """
    Read raw EyeLink eye-tracking data from an EDF file.

    Parameters:
        datapath (str, optional): The directory path where the EDF files are located. 

    Returns A tuple containing three elements:
        elsamples (pd.Dataframe): A dataframe containing samples data from the EDF file.
        elevents (pd.Dataframe): A dataframe containing events data from the EDF file.
        elnotes (pd.Dataframe): A dataframe containing message data from the EDF file.
    """
    logger = logging.getLogger(__name__)
    try:
        check_directory(datapath)
    except FileNotFoundError as error:
        logger.warning("Directory not found while reading raw EyeLink data. Error: %s", error)

    elsamples, elevents, elnotes = edfread.read_edf(os.path.join(datapath, findFile(datapath,'.EDF')[0]))
    
    return (elsamples,elevents,elnotes)
    
    
def import_el(subject, participant_info, datapath='/data/'):
    """
    This function imports EyeLink eyetracking data for a specific subject from the specified 'datapath'.
    It loads and preprocesses the raw eyetracking data files, including individual samples, fixation and 
    saccade definitions, and messages/notes associated with each trial. The function handles issues such as 
    sampling time above 1*e100, negative time values, and incorrect time ordering. It also determines which 
    eye was recorded and preprocesses gaze components and pupil area.

    Parameters:
        subject (str): The subject ID.
        participant_info (pd.DataFrame): DataFrame containing participant information.
        datapath (str, optional): The directory path where the Eyelink eye-tracking data is located.

    Returns: A tuple containing three elements:
        elsamples (pd.DataFrame): DataFrame containing samples data.
        elmsgs (pd.DataFrame): DataFrame containing messages data.
        elevents (pd.DataFrame): DataFrame containing event data.
    """
    assert(type(subject)==str)
    logger = logging.getLogger(__name__)

    try:
        check_directory(datapath)
    except FileNotFoundError as error:
        logger.warning("Directory not found. Error: %s", error)     
    
    elsamples,elevents,elnotes = raw_el_data(datapath)
    
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
    logger.warning('Marking as NaN %.4f%% due to other errors (e.g. lost eye / target)'%(100*np.mean((elsamples.errors!=0))))
    
    #elsamples = elsamples.loc[elsamples.errors == 0]
    elsamples.loc[elsamples.errors != 0,["gx_left","gy_left","gx_right","gy_right"]] = np.NaN
    
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
    elsamples['smpl_time'] = elsamples['time'] / 1000 
    elnotes['msg_time']    = elnotes['time'] / 1000
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
    
    elmsgs = elmsgs.drop(elmsgs.index[elmsgs.isnull().all(1)])
    
    return elsamples, elmsgs, elevents
    

#%% GENERAL DATA LOADING AND IMPORT

def load_and_regress_preprocessed_data(participant_info, datapath='/data/', excludeID=None, cleaned=True):
    """
    Loads eye-tracking data for multiple participants from preprocessed CSV files. This step also
    regresses the eyetrackers so that the timestamps for TrackPixx match those of EyeLink.
    This is formerly "be_load".

    Parameters:
        participant_info (pd.DataFrame): A DataFrame containing participant information, including their IDs.
        datapath (str, optional): The base directory where participant data is stored.
        excludeID (list, optional): A list of participant IDs to exclude from loading.
        cleaned (bool, optional): If True, load cleaned samples; if False, load raw samples. Default is True.

    Returns:
        A tuple containing three pandas DataFrames:
            - etsamples (pd.DataFrame): DataFrame containing eye-tracking samples data.
            - etmsgs (pd.DataFrame): DataFrame containing eye-tracking messages data.
            - etevents (pd.DataFrame): DataFrame containing eye-tracking events data.

    Example:
        etsamples, etmsgs, etevents = load_et_data(participant_info, datapath, excludeID=['sub-010', 'sub-011'])
    """
    
    logger = logging.getLogger(__name__)
    etsamples = pd.DataFrame()
    etmsgs= pd.DataFrame()
    etevents = pd.DataFrame()

    for subject in participant_info.ID.unique():
        preprocessed_folder_path = os.path.join(datapath, subject, 'preprocessed')

        # Exclude participants
        if excludeID is not None and subject in excludeID:
            logger.warning('Warning. Skipping subject ID: %s', subject)
            continue
        # Check whether each participant in the reference file has corresponding eyetracking files.
        if not os.path.exists(preprocessed_folder_path):
            logger.warning('Warning. No folder found for subject ID %s in %s', subject, datapath)
            continue
        
        logger.warning('Loading subject ID: %s ...', subject)
        
        for et in ['el', 'tpx']:
            try:
                if cleaned:
                    filename_samples = f"{et}_cleaned_samples.csv"
                else:
                    filename_samples = f"{et}_samples.csv"
                filename_msgs    = f"{et}_msgs.csv"
                filename_events  = f"{et}_events.csv"
                
                etsamples = pd.concat([etsamples, pd.read_csv(os.path.join(preprocessed_folder_path, filename_samples)).assign(subject=subject, eyetracker=et)], ignore_index=True, sort=False)
                etmsgs    = pd.concat([etmsgs, pd.read_csv(os.path.join(preprocessed_folder_path, filename_msgs)).assign(subject=subject, eyetracker=et)], ignore_index=True, sort=False)
                etevents  = pd.concat([etevents, pd.read_csv(os.path.join(preprocessed_folder_path, filename_events)).assign(subject=subject, eyetracker=et)], ignore_index=True, sort=False)

                # FIXME do we still need this part? Does this not already happen elsewhere?
                # t0 = elmsgs.query("condition=='Instruction'&exp_event=='BEGINNING_start'").msg_time.values
                # if len(t0)!=1:
                #     raise error
                    
                # elsamples.smpl_time = elsamples.smpl_time - t0
                # elmsgs.msg_time= elmsgs.msg_time - t0
                # elevents.start_time = elevents.start_time- t0
                # elevents.end_time = elevents.end_time- t0

            except FileNotFoundError as error:
                logger.critical('Warning: data for %s eyetracker not found!\n %s', et, error)
                continue
        # Regress            
        etsamples, etevents, etmsgs = regress_eyetracker(etsamples, etevents, etmsgs, subject)

        etevents.type = etevents.type.str.lower()
        etsamples.type = etsamples.type.str.lower()
    return etsamples, etmsgs, etevents


def load_data(datapath, datatype, subject=None, eyetracker=None, outputprefix='', sep=";", cleaned=True):
    """
    Load and merge CSV files from multiple subdirectories or a specific subject directory.

    Parameters:
        datapath (str): Path to the main directory containing subdirectories with CSV files.
        datatype (str): Type of CSV file (`etdata` or name of participant info file, e.g. `participant_info`).
        subject (str, optional): Subject identifier for loading data from a specific subject directory.
        eyetracker (str, optional): Output of which eyetracker (el or tp) for loading subject data.
        outputprefix (str, optional): Prefix for the output file names.
        cleaned (bool, optional): Flag to load cleaned or uncleaned data for subject data.

    Returns:
        all_data (pd.DataFrame): Merged DataFrame containing data from all CSV files.
    """
    logger = logging.getLogger(__name__)
    all_data = pd.DataFrame()

    if datatype == 'participant_info':
        # Load participant information
        for root, dirs, files in os.walk(datapath):
            for file in files:
                if file.endswith(datatype + '.csv'):
                    file_path = os.path.join(root, file)
                    data = pd.read_csv(file_path, sep=sep)
                    logger.info("Processing %s", file_path)
                    all_data = pd.concat([all_data, data])
    else:
        # Load subject data
        preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
        et = outputprefix + eyetracker

        try:
            if cleaned:
                filename_samples = str(et) + '_cleaned_samples.csv'
            else:
                filename_samples = str(et) + '_samples.csv'
            filename_msgs = str(et) + '_msgs.csv'
            filename_events = str(et) + '_events.csv'

            etsamples = pd.read_csv(os.path.join(preprocessed_path, filename_samples))
            etmsgs = pd.read_csv(os.path.join(preprocessed_path, filename_msgs))
            etevents = pd.read_csv(os.path.join(preprocessed_path, filename_events))

            all_data = {'samples': etsamples, 'msgs': etmsgs, 'events': etevents}

        except FileNotFoundError as e:
            print(e)
            raise e

    return all_data


def load_participants(datapath, filename="participant_info"):
    """
    Read and process participant information from a CSV file.
        
    Parameters:
        datapath (str): Path to where the participant info is stored.
        filename (str): Name of the file
    Returns:
        participant_info (pd.DataFrame): A dataframe with participant information.
    """
    participant_info = load_data(datapath, filename)
    participant_info['ID'] = participant_info['ID'].astype(str).str.zfill(3)
    participant_info['ID'] = 'sub-' + participant_info['ID']
    return participant_info
