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

#elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)
elsamples, elmsgs,elevents= import_el('VP1')

#%%


plt.figure()
plt.plot(elsamples.smpl_time,elsamples.gy,'o')
#%%
for k,row in elmsgs.query('condition=="GRID"').iterrows():
    if ~np.isnan(row['posy']):
        plt.text(row['msg_time'],0,'%.2f'%(row['posy']))

for k,row in elmsgs.query('condition=="SMOOTH"').iterrows():
    if ~np.isnan(row['angle']):
        plt.text(row['msg_time'],0,'%.2f'%(row['angle']))

#%% SMOOTH
