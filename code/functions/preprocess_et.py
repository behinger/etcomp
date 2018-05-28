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

import os


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#%% Zum testen

# specify subject

if False:
    subject = 'inga_3'
    datapath='/net/store/nbp/projects/etcomp/pilot'

    # filepath for preprocessed folder
    preprocessed_path = os.path.join(datapath, subject, 'preprocessed')

    et = 'el'

#%%
    
def preprocess_et(et,subject,datapath='/net/store/nbp/projects/etcomp/',load=False,save=False,eventfunctions=(make_blinks,make_saccades,make_fixations)):    
    # Output:     3 cleaned dfs: etsamples, etmsgs, etevents
    
    
    logging.info('Starting to preprocess data ...')
    
    # load already calculated df
    if load:
        logging.info('Load data from file ...')
        try:
            etsamples,etmsgs,etevents = load_file(et,subject,datapath)
            return(etsamples,etmsgs,etevents)
        except:
            logging.warning('Error: Could not read file')
        
    # import according to the type of eyetracker
    if et == 'pl':
        logging.debug('Caution: etevents might be empty')
        etsamples,etmsgs,etevents = import_pl(subject=subject,datapath=datapath)
    elif et == 'el':
        etsamples,etmsgs,etevents = import_el(subject=subject,datapath=datapath)
        
        
    # Mark bad samples
    logging.info('Marking bad samples')
    etsamples = detect_bad_samples(etsamples)
    
    # Detect events
    # by our default first blinks, then saccades, then fixations
    logging.info('Making event df')
    for evtfunc in eventfunctions:
        logging.info('Events: calling %s',evtfunc.__name__)
        etsamples, etevents = evtfunc(etsamples, etevents, et)
    
    # Each sample has a column 'type' (blink, saccade, fixation)
    # which is set according to the event df
    logging.info('Add events to each sample')
    etsamples = add_events_to_samples(etsamples,etevents)
    
    # Samples get removed from the samples df
    # because of outside monitor, pupilarea Nan, negative sample time
    
    #logging.info('Removing bad samples')
    #etsamples = remove_bad_samples(etsamples)
    
    
    # in case you want to save the calculated results
    if save:
        save_file([etsamples,etmsgs,etevents],et,subject,datapath)
        logging.debug('Done - saving')
    
    
    return etsamples, etmsgs, etevents
    

