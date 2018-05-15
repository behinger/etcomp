#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 12 13:58:59 2018

@author:   kgross
"""
# playing around with el blink dection

import functions.add_path
import numpy as np
import pandas as pd
import math
import time

import os,sys,inspect

import os
import matplotlib.pyplot as plt
from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import functions.nbp_pupilhelper as nbp_pl
import functions.etcomp_parse as parse
import functions.detect_events as events
#import functions.pl_surface as pl_surface

# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib

   
#%% HELPERS
    
def findFile(path,ftype):
    # finds file for el edf
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out)
  
#%% EYELINK

subject = 'inga_3'
datapath='/net/store/nbp/projects/etcomp/pilot'
# filepath for preprocessed folder
preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
# Load edf
filename = os.path.join(datapath,subject,'raw')

# elsamples:  contains individual EL samples
# elevents:   contains fixation and saccade definitions
# elnotes:    contains notes (meta data) associated with each trial
elsamples, elevents, elnotes = edf.pread(os.path.join(filename,findFile(filename,'.EDF')[0]), trial_marker=b'')

  
#%% Checking blink_id



# Probably not very interesting
elevents = events.el_make_events(subject)

plt.figure()
plt.plot(elevents.index, elevents.start, 'x', color='b')
plt.plot(elevents.index, elevents.end, 'x', color='b')

plt.plot(elevents.query("type=='blink'").index, elevents.query("type=='blink'").start, 'x', color='r')
plt.plot(elevents.query("type=='blink'").index, elevents.query("type=='blink'").end, 'x', color='r')

plt.plot(elevents.query("type=='fixation'").index, elevents.query("type=='fixation'").start, 'x', color='g')
plt.plot(elevents.query("type=='fixation'").index, elevents.query("type=='fixation'").end, 'x', color='g')

plt.plot(elevents.query("type=='saccade'").index, elevents.query("type=='saccade'").start, 'x', color='y')
plt.plot(elevents.query("type=='saccade'").index, elevents.query("type=='saccade'").end, 'x', color='y')


  
#%% 

   # remove to large pa    
    # TODO : we dropped this cause pa mostly look good after removing pa == 0 
    # check pa / diameter large values inga_3 end
    # Pupil Area is unreasonably large
    # As there will be very different absolute pa sizes, we will do outlier detection ? 
#    # keep only the ones that are within +3 to -3 standard deviations
#    marked_samples['too_large_pa'] = np.abs(etsamples.pa-np.nanmean(etsamples.pa))>(3* (np.nanstd(etsamples.pa)))
#    
#    # add columns to the samples df
#    marked_samples = pd.concat([etsamples, marked_samples], axis=1)
#
#    plt.figure()
#    plt.plot(etsamples['smpl_time'], etsamples['pa'], 'x', color='b')
#    plt.plot(marked_samples.query('too_large_pa==1')['smpl_time'], marked_samples.query('too_large_pa==1')['pa'], 'o', color='r')
#    etsamples['pa'].describe()
    



  
#%% 



