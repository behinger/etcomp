#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 09:05:19 2018

@author: behinger
"""


import functions.add_path
import os

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import functions.make_df as  make_df
import functions.ANALYSIS_get_condition_df as get_condition_df


#%%
subject = 'VP3'
datapath = '~/etcomp/local/data/'
etsamples = pd.DataFrame()
etmsgs= pd.DataFrame()
etevents = pd.DataFrame()
for et in ['el','pl']:
    for outputtype in ['','hmm_']:
        elsamples, elmsgs, elevents = helper.load_file(et,subject,datapath=datapath,outputprefix=outputtype)
        t0 = elmsgs.query("condition=='Instruction'&exp_event=='BEGINNING_start'").msg_time
        if t0.empty:
            raise error
        elsamples.smpl_time = elsamples.smpl_time - t0
        elmsgs.msg_time= elmsgs.msg_time - t0
        elevents.start_time = elevents.start_time- t0
        elevents.end_time = elevents.end_time- t0
        if outputtype == '':
            outputtype='engbert'
        elif outputtype=='hmm_':
            outputtype='hmm'
        etsamples = pd.concat([etsamples,elsamples.assign(eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
        etmsgs    = pd.concat([etmsgs,      elmsgs.assign(eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
        etevents  = pd.concat([etevents,  elevents.assign(eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
        
#%%
(ggplot(etsamples.query("smpl_time<2"),aes(x="smpl_time",y="gx",color="type"))+
             geom_point()+
             facet_grid("eyetracker~algorithm")
)
