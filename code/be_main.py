#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 15:49:18 2018

@author: behinger
"""

import functions.add_path
import os

import functions.plotnine_theme
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.et_make_df as  make_df
import functions.et_condition_df as condition_df

import BLINK
import SMOOTHPURSUIT
#%%
subject = 'VP3'
datapath = '~/etcomp/local/data/'
#datapath = '/net/store/nbp/projects/etcomp/'
etsamples = pd.DataFrame()
etmsgs= pd.DataFrame()
etevents = pd.DataFrame()
for et in ['el','pl']:
    for outputtype in ['hmm_']:
        elsamples, elmsgs, elevents = helper.load_file(et,subject,datapath=datapath,outputprefix=outputtype)
        t0 = elmsgs.query("condition=='Instruction'&exp_event=='BEGINNING_start'").msg_time.values
        if len(t0)!=1:
            raise error
        elsamples.smpl_time = elsamples.smpl_time - t0
        elmsgs.msg_time= elmsgs.msg_time - t0
        elevents.start_time = elevents.start_time- t0
        elevents.end_time = elevents.end_time- t0
        
        
        outputtype='hmm'
        
        etsamples = pd.concat([etsamples,elsamples.assign(subject=subject,eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
        etmsgs    = pd.concat([etmsgs,      elmsgs.assign(subject=subject,eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
        etevents  = pd.concat([etevents,  elevents.assign(subject=subject,eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)

        
#%% Do Blink Analysis
blink= condition_df.get_condition_df(data=(etsamples,etmsgs,etevents),condition="BEEP")
BLINK.plot_count(blink)
BLINK.plot_duration(blink)

#%% Do Smooth Pursuit Analysis
smooth = condition_df.get_condition_df(data=(etsamples,etmsgs,etevents),condition="SMOOTHPURSUIT")
etmsgs.query("condition=='SMOOTH'&exp_event=='start'")