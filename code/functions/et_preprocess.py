#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functions.add_path
import logging

from functions.detect_events import make_blinks, make_saccades,make_fixations
from functions.detect_bad_samples import detect_bad_samples,remove_bad_samples
from functions.et_helper import add_events_to_samples
from functions.et_helper import load_file, save_file
from functions.et_make_df import make_events_df
import functions.et_helper as helper



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
        from functions.et_import import import_el
        etsamples, etmsgs, etevents = import_el(subject=subject, participant_info=participant_info, datapath=datapath, **kwargs)
    elif et =="tpx":
        from functions.et_import import import_tpx
        etsamples, etmsgs, etevents = import_tpx(subject=subject, participant_info=participant_info, datapath=datapath, **kwargs)
    else:
        raise ValueError("Unknown eyetracker! 'et' value must be 'el'for EyeLink or 'tpx' for TrackPixx!") 


    # Detect and mark bad samples
    logger.debug('Marking bad eyetracking samples ...')
    etsamples = detect_bad_samples(etsamples)


    # Detect events
    ## by our default first blinks, then saccades, then fixations
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
