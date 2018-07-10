#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 13:38:13 2018

@author: kgross
"""

import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_plotting as etplot
import functions.et_preprocess as preprocess
import functions.et_make_df as make_df
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.pl_detect_blinks as pl_blinks
import functions.et_helper as  helper

from functions.detect_events import make_blinks,make_saccades,make_fixations



subject = 'VP1'
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=False,eventfunctions=(make_blinks,make_saccades,make_fixations))

et_str = 'el'
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents

plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')

plt.plot(etsamples.query('type=="blink"')['smpl_time'],etsamples.query('type=="blink"')['gx'],'o')
plt.plot(etsamples.query('type=="saccade"')['smpl_time'],etsamples.query('type=="saccade"')['gx'],'o')
plt.plot(etsamples.query('type=="fixation"')['smpl_time'],etsamples.query('type=="fixation"')['gx'],'o')
plt.legend(['sample','blink','saccade','fixation'])

plt.title(et_str)
plt.ylim([-40,40])