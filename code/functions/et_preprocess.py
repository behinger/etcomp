#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import pandas as pd

from functions.detect_events import make_blinks, make_saccades, make_fixations
from functions.detect_bad_samples import detect_bad_samples, remove_bad_samples
from functions.et_helper import add_events_to_samples, load_file, save_file, check_directory
from functions.et_import import import_el, import_tpx
from functions.et_make_df import make_events_df


def preprocess_et(et, subject, participant_info, datapath='/data/', load=False, save=False, eventfunctions=(make_blinks,make_saccades,make_fixations), outputprefix='', **kwargs):
    """
    A function for loading and preprocessing EyeLink and TrackPixx eye-tracking data. It exectutes the following steps: 

    1. It imports sample, message, and event data. 
    2. Detects and marks bad samples.
    3. Detects events
    4. Adds event data to sample data
    5. Removed bad samples

    Optionally, you can load already preprocessed data or save the data you have preprocessed with this function. 

    Parameters:
        et (str): The type of eye tracker, must be 'el' (for EyeLink) or 'tpx' (for TrackPixx).
        subject (str): Identifier for the subject.
        participant_info (pd.DataFrame): A dataframe with participant information, specifically containing dominant eye information.
        datapath (str): Path to the directory containing eye-tracking data files. Default is '/data/'.
        load (bool): Whether to load previously calculated dataframes. Default is False.
        save (bool): Whether to save the preprocessed data. Default is False.
        eventfunctions (tuple): Tuple of functions for detecting events such as blinks, saccades, and fixations. Default is (make_blinks, make_saccades, make_fixations).
        outputprefix (str): Prefix for output filenames. Default is an empty string.
        **kwargs: Additional keyword arguments passed to the eye tracker import functions.

    Returns:
        A tuple containing three cleaned dataframes: 
        cleaned_etsamples (pd.DataFrame): A dataframe containing preprocessed and filtered sample report data.
        etmsgs (pd.DataFrame): A dataframe containing the message report information (e.g. tasks, triggers).
        etevents (pd.DataFrame): A dataframe containing event report information (this will be empty for TrackPixx).

    Example:
        cleaned_etsamples, etmsgs, etevents = preprocess_et(et='el',
                                                             subject='sub-001',
                                                             participant_info=id_df,
                                                             datapath='/path/to/data/',
                                                             load=False,
                                                             save=True,
                                                             eventfunctions=(make_blinks, make_saccades, make_fixations),
                                                             outputprefix='preprocessed_')
    """
    logger = logging.getLogger(__name__)
    
    # Load preprocessed data if they have already been generated before.
    if load:
        logger.info('Loading eyetracking data from file ...')
        try:
            etsamples, etmsgs, etevents = load_file(et, subject, datapath, outputprefix=outputprefix)
            return(etsamples, etmsgs, etevents)
        except:
            logger.warning('Error: Could not read file.')


    # Import eyetracking data based on the eyetracker type (EyeLink or TrackPixx).
    logger.debug("Importing eyetracking data ...")
    if et == 'el':
        etsamples, etmsgs, etevents = import_el(subject=subject, participant_info=participant_info, datapath=datapath, **kwargs)
    elif et =="tpx":
        etsamples, etmsgs, etevents = import_tpx(subject=subject, participant_info=participant_info, datapath=datapath, **kwargs)
    else:
        raise ValueError("Unknown eyetracker! 'et' value must be 'el'for EyeLink or 'tpx' for TrackPixx!") 


    # Detect and mark bad samples
    logger.debug('Marking bad eyetracking samples ...')
    etsamples = detect_bad_samples(etsamples)


    # Detect events
    ## by default first blinks, then saccades, then fixations
    logger.debug('Making event dataframe ...')
    for evtfunc in eventfunctions:
        logger.debug('Events: calling %s', evtfunc.__name__)
        etsamples, etevents = evtfunc(etsamples, etevents, et)
        
    ## Make a nice etevent df
    etevents = make_events_df(etevents)
    
    ## Each sample has a column 'type' (blink, saccade, fixation)
    ## which is set according to the event df
    logger.debug('Adding events to each sample ...')
    etsamples = add_events_to_samples(etsamples,etevents)


    # Remove data
    ## Samples get removed from the samples df
    ## because of they're outside monitor bounds, pupilarea is Nan, negative sample time
    logger.info('Removing bad samples ...')
    cleaned_etsamples = remove_bad_samples(etsamples)


    # Saving the file if you want to keep the calculated results
    if save:
        logger.info('Saving preprocessed et data ...')
        save_file([etsamples, cleaned_etsamples, etmsgs, etevents], et, subject, datapath, outputprefix=outputprefix)

    return cleaned_etsamples, etmsgs, etevents



def load_and_process_all_et_data(participant_info, et, datapath='/data/', excludeID=None):
    """
    Preprocesses eye-tracking data for multiple participants and combines the results into a DataFrames.
    Formerly 'be_load'.

    This function iterates over the participant IDs, loads and preprocesses the corresponding eye-tracking data files, 
    and aggregates the cleaned samples, messages, and events data into separate pandas DataFrames.

    Parameters:
        participant_info (pd.DataFrame): A DataFrame containing participant information, including their IDs.
        et (str): The type of eye-tracker data to preprocess and load ('el' for Eyelink, 'tpx' for TrackPixx).
        datapath (str, optional): The base directory where participant data is stored.
        excludeID (list, optional): A list of participant IDs to exclude from preprocessing.

    Returns:
        A tuple containing three pandas DataFrames:
            - cleaned_etsamples (pd.DataFrame): DataFrame containing cleaned eye-tracking samples data.
            - etmsgs (pd.DataFrame): DataFrame containing eye-tracking messages data.
            - etevents (pd.DataFrame): DataFrame containing eye-tracking events data.
    """
    logger = logging.getLogger(__name__)
    cleaned_etsamples = pd.DataFrame()
    etmsgs= pd.DataFrame()
    etevents = pd.DataFrame()

    for subject in participant_info.ID.unique():
        # Exclude participants
        if excludeID is not None and subject in excludeID:
            logger.warning('Warning. Skipping subject ID: %s', subject)
            continue
        # Check whether each participant in the reference file has corresponding eyetracking files.
        if not os.path.exists(datapath):
            logger.warning('Warning. No folder found for subject ID %s in %s', subject, datapath)
            continue
        logger.warning('Reading and preprocessing subject ID: %s', subject)
        raw_folder_path = os.path.join(datapath, subject, 'raw')
        
        try:
            check_directory(raw_folder_path)
            cleaned_etsamples, etmsgs, etevents = preprocess_et(et=et,
                                                                subject=subject,
                                                                participant_info=participant_info,
                                                                datapath=raw_folder_path,
                                                                load=False,
                                                                save=True,
                                                                eventfunctions=(make_blinks, make_saccades, make_fixations),
                                                                outputprefix='preprocessed_')
        except FileNotFoundError as error:
            logger.warning("Directory not found. Error: %s", error)

    return cleaned_etsamples, etmsgs, etevents # FIXME do I want to have this as a result? We only ever need the saved data?
