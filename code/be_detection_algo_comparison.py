#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 09:05:19 2018

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

import LARGE_GRID
#%%
subject = 'VP3'
datapath = '~/etcomp/local/data/'
#datapath = '/net/store/nbp/projects/etcomp/'
etsamples = pd.DataFrame()
etmsgs= pd.DataFrame()
etevents = pd.DataFrame()
etgrid   = pd.DataFrame()
for et in ['el','pl']:
    for outputtype in ['','hmm_']:
        elsamples, elmsgs, elevents = helper.load_file(et,subject,datapath=datapath,outputprefix=outputtype)
        rawGRID   = condition_df.get_condition_df([subject], [et], condition='LARGE_GRID',outputprefix = outputtype,datapath=datapath)
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
        etgrid  = pd.concat([etgrid,  rawGRID.assign(eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
        
        
#%%
tstart =110
tdur =25
(ggplot(etsamples.query("algorithm=='hmm' & smpl_time>%i & smpl_time<%i"%(tstart,tstart+tdur)),aes(x="smpl_time",y="gx",color="type"))+
             geom_point()+xlab('time [s]')+ylab('X-Position [visual °]')+#+ylim([-20,20])+
             facet_grid("eyetracker~.")
)

#%% Large Grid Performance
ggplot(complete_large_grid_df, aes(x='mean_gx', y='mean_gy', color='factor(posx*posy)')) \
        + geom_point((aes(size=10, shape=10)), alpha=1.0) \
        + geom_point(aes(x='posx', y='posy', color='factor(posx*posy)'), alpha=0.4) \
        + ggtitle('Mean fixation gaze vs displayed element points')



 # plot eyetracker vs  mean accuracy over all blocks
(ggplot(etgrid, aes(x='eyetracker', y='accuracy', color='algorithm')) +
                  geom_point(position=position_dodge(width=0.7)))
etgrid.groupby(['eyetracker','algorithm']).apply(lambda row: np.mean(row.accuracy,trim=0.2))
