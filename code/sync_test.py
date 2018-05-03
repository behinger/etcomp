# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
import os,sys,inspect

from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import os
import matplotlib.pyplot as plt
import functions.nbp_pupilhelper as nbp_pl
import functions.etcomp_parse as parse
import functions.et_plotting as etplot
import functions.et_import as load

# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib

#%%

# load and preprocess et data

# specify subject
subject = 'inga_2'

# load pl data
original_pldata = load.raw_pl_data(subject)

# TODO: this is a little inconsistent
# preprocess original_pldata to get 3 dataframes: samples msgs epochs
plsamples, plmsgs, plepochs = load.preprocess_pl(original_pldata)


# load **preprocessed** el data as 3 dataframes: samples msgs epochs
elsamples, elmsgs, elepochs = load.preprocess_el(subject)

#%%

# We are going to have 5 types of Dataframes:
# sample, msgs, events, epochs und for each condition a df FULL for pl and el respectively 
# for more details please have a look at the "overview dataframes pdf"

# have a look at the data

# samples df
elsamples.dtypes
elsamples.head()
plsamples.dtypes

# msgs df
elmsgs.dtypes
plmsgs.dtypes

# TODO: Why do we find a missmatch here?
elmsgs.condition.value_counts()
plmsgs.condition.value_counts()


# epochs df
elepochs.head()
elepochs.dtypes

# look how many samples that can be used for each condition
elepochs.condition.value_counts()
plepochs.condition.value_counts()

# How to query for samples from a specific condition
# print(pl_epochs.query('condition=="SMOOTH"'))

   
#%% SANITY CHECKS



   
#%%

# Looking at dilation data

# EL
etplot.plot_diam(elepochs, measure='pa', query='condition=="DILATION" & block==1 & lum==1')

# PL
etplot.plot_diam(plepochs, measure='diameter', query='condition=="DILATION" & block==1 & lum==1')


#%%

#%%

#%%   

# Plotting

# plot pl against el
# if fixationcross presented at posx==960
# x-axis: td time 
# y-axis: horiz. component of gaze 
etplot.plotTraces([plepochs,elepochs],query = 'posx==960')

etplot.plotTraces([pl_matched_data,el_matched_data],query = 'element == 15 & block == 1',figure=False)


#%% ---- Have a look at the surface CSV files
# In the end they look super bad, the eyes are not fused properly.
surfacepath = os.path.join(filename,'exports','000','surfaces')
surface_files = [os.path.join(surfacepath,f) for f in findFile(surfacepath,'.csv',returnN=-1)]

#pd.read_csv(os.path.join(file,surface_files[1])) # surface_gaze_distribution how many samples on surface, completely usesless
#pd.read_csv(os.path.join(file,surface_files[2])) # surface_events surface enter/exit, completly usesless for us


pd.read_csv(os.path.join(file,surface_files[3])) #srf_positons_unnamed <- could be usefule for intrinsic camera undistortion
pldata_surface = pd.read_csv(os.path.join(file,surface_files[4])) #gaze_positions_on_surface_unnamed <- thats the meat

plt.figure
plt.plot(pldata_surface['gaze_timestamp'],pldata_surface['x_norm'])

plt.figure
plt.plot(pldata_surface['x_norm'],pldata_surface['y_norm'],'o')


#%%

# convert pl gaze data to same scale as EL  :   Is it correct?
pl_matched_data.gx = pl_matched_data.gx*1920


