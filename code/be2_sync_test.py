#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 16:32:16 2018

@author: behinger
"""

import functions.add_path
import numpy as np
import pandas as pd
import os,sys
 
from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import matplotlib.pyplot as plt
import functions.nbp_pupilhelper as nbp_pl
import functions.etcomp_parse as parse
import functions.et_plotting as etplot
import functions.et_import as load
from functions.et_import import make_epochs
from functions.detect_blinks import pupil_detect_blinks

# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib

#%%

# load and preprocess et data

# specify subject
subject = 'inga_5'

# load pl data
original_pldata = load.raw_pl_data(subject)

plsamples, plmsgs = load.preprocess_pl(subject, recalib=True,surfaceMap=True,save=True,recalculate=True)
# approx only
plsamples.gx = plsamples.gx*(1920 - 2*18) # minus white border of marker
plsamples.gy = plsamples.gy*(1080- 2*18)


elsamples, elmsgs = load.preprocess_el(subject)
elsamples.loc[elsamples.gx>5000,:] = np.nan

condquery = 'condition == "DILATION" & exp_event=="lum"'
condquery = 'condition == "FREEVIEW" & exp_event=="trial"'

condquery = 'condition == "SMOOTH" & exp_event=="trialstart"'

td = [-1, 1]
elepochs = make_epochs(elsamples,elmsgs.query(condquery), td=td)
plepochs = make_epochs(plsamples,plmsgs.query(condquery), td=td)


etplot.plotTraces([plepochs,elepochs], y='gx',query='posx==722')

etplot.plotTraces([plepochs,elepochs], y='gx',query='block == 6')

etplot.plotTraces([plepochs], x='gx',y='gy',query='')


etplot.plotTraces([plepochs], y='pa',query='lum>0')


etplot.plotTraces([plepochs.query('prevlum==128'),plepochs.query('prevlum==0'),plepochs.query('prevlum==255')], y='pa')


# Do the 5x5 grid
condquery = 'condition == "DILATION" & exp_event=="lum"'

td = [-1, 3]
elepochs = make_epochs(elsamples,elmsgs.query(condquery), td=td)
plepochs = make_epochs(plsamples,plmsgs.query(condquery), td=td)



def add_prevlum(data):
    prevlum = 128
    currlum = 128
    prevlumlist = []
    for k in range(data.shape[0]):
        if not data.lum.iloc[k]== currlum:
            prevlum = currlum
            currlum = data.lum.iloc[k]
            
        prevlumlist.append(prevlum)
        
    data['prevlum'] = prevlumlist
    return(data)

elepochs = add_prevlum(elepochs)
plepochs = add_prevlum(plepochs)

from bokeh.models import Range1d

p = []

for lum in np.sort(plepochs.lum.unique()):
    for lumprev in np.sort(plepochs.prevlum.unique()):
        try:
            pl =etplot.plotTraces([plepochs,  elepochs], width=400,height=400,y='pa',query='prevlum==%i&lum==%i'%(lumprev,lum),showplot=False)
            pl.y_range=Range1d(0,400)
            p.append(pl)
        except:
            p.append(None)
    
from bokeh.layouts import gridplot
from bokeh.plotting import figure,show

pl = gridplot(p,ncols=5)
show(pl)




etplot.plotTraces([elepochs.query('prevlum==0'),elepochs.query('prevlum==255')], width=400,height=400,y='pa',query='lum==%i'%(255))
