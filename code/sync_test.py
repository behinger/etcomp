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
subject = 'inga_3'

# load pl data
# original_pldata = load.raw_pl_data(subject)


# preprocess pl_pldata to get 2 dataframes: samples, msgs
plsamples, plmsgs = load.preprocess_pl(subject)

# load **preprocessed** el data as 2 dataframes: samples msgs
elsamples, elmsgs = load.preprocess_el(subject)


# remove bad_samples (gaze outside monitor)
plsamples = load.remove_bad_samples(plsamples)
# elsamples = load.remove_bad_samples(elsamples)


# epoch etdata according to query
condquery = 'condition == "DILATION" & exp_event=="lum"&block == 1'
plepochs = load.make_epochs(plsamples, plmsgs.query(condquery))
elepochs = load.make_epochs(elsamples, elmsgs.query(condquery))


#%%

# We are going to have 5 types of Dataframes:
# sample, msgs, events, epochs und for each condition a df FULL for pl and el respectively 
# for more details please have a look at the "overview dataframes pdf"

# have a look at the data

# samples df
plsamples.info()
plsamples.describe()
elsamples.info()
elsamples.describe()


# msgs df
plmsgs.info()
plmsgs.describe()
elmsgs.info()
elmsgs.describe()

# TODO: Why do we find a missmatch here?
elmsgs.condition.value_counts()
plmsgs.condition.value_counts()


# epochs df
elepochs.info()
elepochs.describe()
plepochs.info()
plepochs.describe()


# look how many samples that can be used for each condition
plepochs.condition.value_counts()
elepochs.condition.value_counts()

   
#%% SANITY CHECKS

# msgs EL
elmsgs.info()
set(elmsgs['pic_id'].unique()) - set(plmsgs['pic_id'].unique()) 

   
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


