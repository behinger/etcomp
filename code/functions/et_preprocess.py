#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 17:16:15 2018

@author: kgross
"""

import functions.add_path
#import pandas as pd
#import numpy as np
#import os

from functions.detect_events import make_blinks,make_saccades,make_fixations
from functions.import_et import import_pl,import_el
from functions.detect_bad_samples import detect_bad_samples,remove_bad_samples
from functions.et_helper import add_events_to_samples
from functions.et_helper import load_file, save_file
from functions.make_df import make_events_df
import functions.et_helper as  helper

import os
import logging

#%%
    
def preprocess_et(et,subject,datapath='/net/store/nbp/projects/etcomp/',load=False,save=False,eventfunctions=(make_blinks,make_saccades,make_fixations),outputprefix=''):    
    # Output:     3 cleaned dfs: etsamples, etmsgs, etevents   
    
    # get a logger for the preprocess function    
    logger = logging.getLogger(__name__)
    
    # load already calculated df
    if load:
        logger.info('Loading et data from file ...')
        try:
            etsamples,etmsgs,etevents = load_file(et,subject,datapath,outputprefix=outputprefix)
            return(etsamples,etmsgs,etevents)
        except:
            logger.warning('Error: Could not read file')

        
    # import according to the type of eyetracker
    logger.debug("Importing et data")
    if et == 'pl':
        logger.debug('Caution: etevents might be empty')
        etsamples,etmsgs,etevents = import_pl(subject=subject,datapath=datapath)
    elif et == 'el':
        etsamples,etmsgs,etevents = import_el(subject=subject,datapath=datapath)
        
        
    # Mark bad samples
    logger.debug('Marking bad et samples')
    etsamples = detect_bad_samples(etsamples)
    
    # Detect events
    # by our default first blinks, then saccades, then fixations
    logger.debug('Making event df')
    for evtfunc in eventfunctions:
        logger.debug('Events: calling %s', evtfunc.__name__)
        etsamples, etevents = evtfunc(etsamples, etevents, et)
        
    # Make a nice etevent df
    etevents = make_events_df(etevents)
    
    # Each sample has a column 'type' (blink, saccade, fixation)
    # which is set according to the event df
    logger.debug('Add events to each sample')
    etsamples = add_events_to_samples(etsamples,etevents)
       
    # Samples get removed from the samples df
    # because of outside monitor, pupilarea Nan, negative sample time
    logger.info('Removing bad samples')
    cleaned_etsamples = remove_bad_samples(etsamples)
    
    
    # in case you want to save the calculated results
    if save:
        logger.info('Saving preprocessed et data')
        save_file([etsamples,cleaned_etsamples, etmsgs,etevents],et,subject,datapath,outputprefix=outputprefix)
    
    
    return cleaned_etsamples, etmsgs, etevents
    

