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

  
#%% 

# el events has column blink (booleans)
elevents.columns


# filter all rows where blink==True
ix_blink = elevents.blink==True
df_only_blinks = elevents.loc[ix_blink]
# we are only interested in when the blink started and ended
df_only_blinks = df_only_blinks.loc[:, ['start', 'end', 'blink']]

# we can plot to see if on and offset are reasonable
plt.plot(elsamples.time, elsamples.pa_right, 'o')
plt.plot(df_only_blinks.start, df_only_blinks.blink, 'o')
plt.plot(df_only_blinks.end, df_only_blinks.blink, 'o')

# plan: lege an samples eine Spalte fuer blinks an, die True ist wenn smpl_time zwischen start und end liegt
# lege weitere Spalte an, die die Blink id hochzaehlt

elsamples['blink'] = False
for bindex,brow in df_only_blinks.iterrows():
    ix =  (elsamples.time>=(brow['start']+100)) & (elsamples.time<(brow['end']+100))
    elsamples['blink'][ix] = True
    


elsamples['blink'].describe()
