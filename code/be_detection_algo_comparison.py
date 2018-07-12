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
        t0 = elmsgs.query("condition=='Instruction'&exp_event=='BEGINNING_start'").msg_time.values
        if len(t0)!=1:
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
tstart = 430
tdur =10
(ggplot(etsamples.query("smpl_time>%i & smpl_time<%i"%(tstart,tstart+tdur)),aes(x="smpl_time",y="gx",color="type"))+
             geom_point()+
             facet_grid("algorithm~eyetracker")
)

#%% Large Grid Performance
complete_large_grid_df = get_condition_df.get_complete_large_grid_df(['VP3'], ['pl','el'],outputprefix='hmm_',datapath=datapath)
#%%
ggplot(complete_large_grid_df, aes(x='mean_gx', y='mean_gy', color='factor(posx*posy)')) \
        + geom_point((aes(size=10, shape=10)), alpha=1.0) \
        + geom_point(aes(x='posx', y='posy', color='factor(posx*posy)'), alpha=0.4) \
        + ggtitle('Mean fixation gaze vs displayed element points')

