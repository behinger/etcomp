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
import functions.detect_events as events
import functions.pl_detect_blinks as detect_blinks

# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib

#%%
# load and preprocess et data

# specify subject
subject = 'inga_3'

#############  PL
# load pl data
# original_pldata = load.raw_pl_data(subject)

# preprocess pl_pldata to get 2 dataframes: samples, msgs
plsamples, plmsgs = load.preprocess_pl(subject, date='2018-05-11', recalculate=True)
plsamples.type.unique()

#############  EL
# load **preprocessed** el data as 2 dataframes: samples msgs
elsamples, elmsgs = load.preprocess_el(subject, date='2018-05-11', recalculate=True)


#%% 
# TODO
# remove bad_samples (gaze outside monitor)
# plsamples = load.remove_bad_samples(plsamples)
# elsamples = load.remove_bad_samples(elsamples)



#%%  EVENTS

#############  PL
# TODO: lets discuss if this is a smart way to do it
# see file detect_events
plevents = events.pl_make_events(plsamples)

# or
plblinkevents = events.pl_make_blink_events(plsamples)
plsaccades = events.detect_saccades_engbert_mergenthaler(plsamples,fs=240)



#############  EL
# TODO: why is time zero???
# well mybe because we dont use el messages?
elevents = events.el_make_events(subject)

# have a look at how many saccades, blinks, fixations
plt.figure()
elevents['type'].value_counts().plot(kind='bar')

plt.figure()
elsacc = elevents.query('type=="saccade"')
elsacc['duration'] = (elsacc['end'] - elsacc['start']).round(2)
elsacc.duration.value_counts().plot(kind='bar')

# Sieht ziemlich anders aus?!?!

# Saccades from Engbert
elsaccades = events.detect_saccades_engbert_mergenthaler(elsamples)
plt.figure()
elsaccades.expanded_duration.value_counts().plot(kind='bar')




#%% EPOCHED

# epoch etdata according to query
condquery = 'condition == "DILATION" & exp_event=="lum"'
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


#%% PUPIL DILATION

# Looking at dilation data

elepochs.lum.unique()


# TODO something is still wrong with dilation

# EL
etplot.plot_diam(elepochs,query='condition=="DILATION" & block==1 & lum==255')

# PL
etplot.plot_diam(plepochs, query='condition=="DILATION" & block==1 & lum==64')



etplot.plotTraces(plepochs, y='pa', query='condition=="DILATION" & lum==64')
etplot.plotTraces(elepochs, y='pa', query='condition=="DILATION" & block==1 & lum==255')


#%%

# Detect Saccades

plsaccades3 = events.detect_saccades_engbert_mergenthaler(plsamples,fs=240)
elsaccades = events.detect_saccades_engbert_mergenthaler(elsamples)



# For plotting only
plsamples['is_saccade'] = False
plsamples['is_saccade_ext'] = False
for bindex,brow in plsaccades3.iterrows():
    # get index of all samples that are +- 100 ms of a detected blink
    ix =  (plsamples.smpl_time>=(brow['raw_start_time'])) & (plsamples.smpl_time<(brow['raw_end_time']))
    # mark them as blink
    plsamples.loc[ix, 'is_saccade'] = True
    
    ix =  (plsamples.smpl_time>=(brow['expanded_start_time'])) & (plsamples.smpl_time<(brow['expanded_end_time']))
    # mark them as blink
    plsamples.loc[ix, 'is_saccade_ext'] = True

plt.figure()
plt.plot(plsamples.smpl_time, plsamples.gx, 'o')
plt.plot(plsamples.query('is_saccade_ext==1')['smpl_time'], plsamples.query('is_saccade_ext==1')['gx']+0.01, 'o')
plt.plot(plsamples.query('is_saccade==1')['smpl_time'], plsamples.query('is_saccade==1')['gx']+0.02, 'o')
plt.plot(plsamples.query('is_blink==1')['smpl_time'], plsamples.query('is_blink==1')['gx']+0.03, 'o')



elsaccades.head()
elsaccades.columns
elsaccades.describe()


#%%

# Plot Blinks PL

plt.plot(plsamples.smpl_time, plsamples.confidence, 'o')
plt.plot(plsamples.query('is_blink==1')['smpl_time'], plsamples.query('is_blink==1')['confidence']+0.01, 'o')
plt.plot(plsamples['smpl_time'], plsamples['blink_id'], 'o')



#%%

#%%

#%%   

# Plotting

# plot pl against el
# if fixationcross presented at posx==960
# x-axis: td time 
# y-axis: horiz. component of gaze 
etplot.plotTraces([plepochs,elepochs],query = 'posx==960')

etplot.plotTraces([plepochs,elepochs],query = 'element == 15 & block == 1',figure=False)


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


