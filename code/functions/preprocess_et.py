#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 17:16:15 2018

@author: kgross
"""

import functions.add_path
import numpy as np

from functions.detect_events import make_blinks,make_saccades,make_fixations
from functions.import_et import import_pl,import_el
from functions.detect_bad_samples import detect_bad_samples,remove_bad_samples
from functions.et_helper import add_events_to_samples
def preprocess_et(et,subject,datapath='/net/store/nbp/projects/etcomp/pilot',load=True,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations)):
    
    if load:
        try:
            etsamples,etmsgs,etevents = load_file(et,subject,datapath)
            return(etsamples,etmsgs,etevents)
        except:
            pass
        
        
    if et == 'pl':
        # etevents might be empty
        etsamples,etmsgs,etevents = import_pl(subject=subject,datapath=datapath)
    elif et == 'el':
        etsamples,etmsgs,etevents = import_el(subject=subject,datapath=datapath)
        
    # Mark bad samples
    print('Marking bad samples')
    etsamples = detect_bad_samples(etsamples)
    
    #Detect events
    # by our default first blinks, then saccades, then fixations
    for evtfunc in eventfunctions:
        print('Events: calling',evtfunc.__name__)
        etsamples,etevents = evtfunc(etsamples,etevents,et)
    
    
    print('Add events to each sample')
    etsamples = add_events_to_samples(etsamples,etevents)
    
    print('Removing bad samples')
    etsamples = remove_bad_samples(etsamples)
    
    
    print('Done - saving')
    save_file([etsamples,etmsgs,etevents],et,subject,datapath)
    
    return(etsamples,etmsgs,etevents)
    
    
def load_file(et,subject,datapath):
    
    return etsamples,etmsgs,etevents

def save_file(data,et,subject,datapath):
    pass



