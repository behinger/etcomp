# -*- coding: utf-8 -*-

import functions.add_path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.make_df as df
import functions.et_helper as  helper
import functions.et_plotting as etplot
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.et_preprocess as preprocess
import functions.pl_detect_blinks as pl_blinks
from functions.detect_events import make_blinks,make_saccades,make_fixations



#%% LOAD DATA and preprocess RAW data for ALL subjects

# to initialize logging
import functions.init_logger
import logging


# loop over the foldernames (subjectnames)
# restricted to subjects that we do not exclude from analysis
# also loop over the et
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
#rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8']
# ['pilot', '007', 'log_files', 'surface', 'VP1', 'VP2', 'VP3', 'VP4', 'VP7', 'VP8', 'VP11', 'VP12', 'VP14', 'VP15']
# ['pilot', '007', 'log_files', 'surface', 'VP1', 'VP7', 'VP8', 'VP11', 'VP12', 'VP14', 'VP15']
rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP1', 'VP2', 'VP7', 'VP8', 'VP11', 'VP12', 'VP14', 'VP15']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    


# get a logger
logger = logging.getLogger(__name__)

# preprocess for all subjects
for subject in subjectnames:
    for et in ets:
        logger.critical(' ')
        logger.critical('Eyetracker: %s    Subject: %s ', et, subject)
        etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))



#%% LOAD DATA and preprocess RAW data for ONE subject
# specify subject
subject = 'VP1'

# preprocess pl data
plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))

# preprocess el data
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))




#%% LOAD preprocessed DATA from csv file

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)


# which et do you want to examine?
et_str = 'pl'
etsamples = plsamples
etmsgs = plmsgs
etevents = plevents
# or
et_str = 'el'
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents


# have a look at time and gx
plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')




#%% Figure to examine which samples we exclude


plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')

plt.plot(etsamples.query('type=="blink"')['smpl_time'],etsamples.query('type=="blink"')['gx'],'o')
plt.plot(etsamples.query('type=="saccade"')['smpl_time'],etsamples.query('type=="saccade"')['gx'],'o')
plt.plot(etsamples.query('type=="fixation"')['smpl_time'],etsamples.query('type=="fixation"')['gx'],'o')
plt.legend(['sample','blink','saccade','fixation'])

plt.title(et_str)
plt.ylim([0,2500])

plt.plot(etsamples.query('neg_time==True')['smpl_time'],etsamples.query('neg_time==True')['gx'],'o')
plt.plot(etsamples.query('outside==True')['smpl_time'],etsamples.query('outside==True')['gx'],'o')
plt.plot(etsamples.query('zero_pa==True')['smpl_time'],etsamples.query('zero_pa==True')['gx'],'o')
















