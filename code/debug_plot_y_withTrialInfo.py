#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 15:49:12 2018

@author: behinger
"""

import functions.add_path
import numpy as np
import pandas as pd
import os 
import matplotlib.pyplot as plt
import functions.et_preprocess as preprocess
from pyedfread import edf
import functions.et_parse as parse
from functions.et_helper import findFile,gaze_to_pandas
from functions.import_et import import_el

#%%

# elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)
# elsamples, elmsgs,elevents= import_el('VP1')


# load preprocessed data for el subject VP1
elsamples, elmsgs, elevents = preprocess.preprocess_et('el','VP1',load=True)
     

       

_etsamples, etmsgs, etevents = preprocess.preprocess_et('pl','VP15',load=True)

datapath='/net/store/nbp/projects/etcomp/'
preprocessed_path = os.path.join(datapath, 'VP15', 'preprocessed')
filename_samples = 'pl_samples.csv'
etsamples = pd.read_csv(os.path.join(preprocessed_path,filename_samples))

plt.figure()
plt.plot(etsamples.smpl_time,etsamples.gy,'o')

#%%

for k,row in etmsgs.query('condition=="FREEVIEW"').iterrows():
    if ~np.isnan(row['trial']):
        #plt.text(row['msg_time'],0,'%s'%(row['exp_event']))
        plt.text(row['msg_time'],0,'%s'%(row['pic_id']))
        
plt.plot(etsamples.query('type=="blink"')['smpl_time'],etsamples.query('type=="blink"')['gy'],'o')
plt.plot(etsamples.query('type=="saccade"')['smpl_time'],etsamples.query('type=="saccade"')['gy'],'o')
plt.plot(etsamples.query('type=="fixation"')['smpl_time'],etsamples.query('type=="fixation"')['gy'],'o')
plt.legend(['sample','blink','saccade','fixation'])        


for k,row in elmsgs.query('condition=="Instruction"').iterrows():
    #if ~np.isnan(row['exp_event']):
        plt.text(row['msg_time'],0,'%s'%(row['exp_event']))


for k,row in elmsgs.query('condition=="GRID"').iterrows():
    if ~np.isnan(row['posy']):
        plt.text(row['msg_time'],0,'%.2f'%(row['posy']))



for k,row in elmsgs.query('condition=="SMALLGRID_BEFORE"').iterrows():
    if ~np.isnan(row['posy']):
        plt.text(row['msg_time'],0,'%.2f'%(row['posy']))

for k,row in elmsgs.query('condition=="SMALLGRID_AFTER"').iterrows():
    if ~np.isnan(row['posy']):
        plt.text(row['msg_time'],0,'%.2f'%(row['posy']))







for k,row in elmsgs.query('condition=="FREEVIEW"').iterrows():
    #if ~np.isnan(row['exp_event']):
    plt.text(row['msg_time'],0,'%s'%(row['exp_event']))


for k,row in elmsgs.query('condition=="SMOOTH"').iterrows():
    if ~np.isnan(row['angle']):
        plt.text(row['msg_time'],0,'%.2f'%(row['angle']))

#%% SMOOTH
