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


# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib

#%%

# load and preprocess et data

# specify subject
subject = 'inga_3'

# load pl data
original_pldata = load.raw_pl_data(subject)

plsamplesuncal, plmsgsuncal = load.preprocess_pl(subject, recalib=False,surfaceMap=False)

plsamples, plmsgs = load.preprocess_pl(subject, recalib=True,surfaceMap=True)
# approx only
plsamples.gx = plsamples.gx*(1920 - 2*18) # minus white border of marker
plsamples.gy = plsamples.gy*(1080- 2*18)


elsamples, elmsgs = load.preprocess_el(subject)
elsamples.loc[elsamples.gx>5000,:] = np.nan

condquery = 'condition == "DILATION" & exp_event=="lum"&block == 1'
condquery = 'condition == "FREEVIEW" & exp_event=="trial"'
condquery = 'condition == "GRID" & exp_event=="element" & block ==4'

td = [0.3, 0.4]
elepochs = make_epochs(elsamples,elmsgs.query(condquery), td=td)
plepochs = make_epochs(plsamples,plmsgs.query(condquery), td=td)


etplot.plotTraces([plepochs,elepochs], y='gx',query='posx==722')

etplot.plotTraces([plepochs,elepochs], y='gx',query='block == 6')

etplot.plotTraces([plepochs,elepochs], x='gx',y='gy',query='')


etplot.plotTraces([plepochs,elepochs], y='diameter',query='lum==0')