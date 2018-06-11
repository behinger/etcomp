# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_plotting as etplot
import functions.et_preprocess as preprocess
import functions.make_df as df
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.pl_detect_blinks as pl_blinks
import functions.et_helper as  helper

from functions.detect_events import make_blinks,make_saccades,make_fixations

import os
import logging

#%% LOGGING

logger = logging.getLogger('sync_test')

# set logging level 
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler(filename=os.path.join('/net/store/nbp/projects/etcomp/log_files', 'preprocess_log_file.log'))
# set handler level
handler.setLevel(logging.DEBUG)
# create a logging format
formatter = logging.Formatter("%(asctime)s - %(name)-55s - %(levelname)-8s - %(message)s", "%Y-%m-%d %H:%M:%S")
# logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


#%% LOAD DATA and preprocess RAW data for ALL subjects

# loop over the foldernames (subjectnames)
# restricted to subjects that we do not exclude from analysis
# also loop over the et
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
rejected_subjects = ['pilot', 'log_files', '007', 'VP11', 'VP8', 'VP13', 'VP1', 'VP2', 'VP3', 'VP4']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['pl', 'el']    

# preprocess for all subjects
for subject in subjectnames:
    for et in ets:
        print()
        print()
        print()
        logger.critical(' ')
        logger.critical('Eyetracker: %s    Subject: %s ', et, subject)
        print()
        etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))



#%% LOAD DATA and preprocess RAW data for ONE subject
# specify subject
subject = 'VP1'

# preprocess pl data
plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))

# preprocess el data
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=False,eventfunctions=(make_blinks,make_saccades,make_fixations))


#%% LOAD preprocessed DATA from csv file

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)


# which et do you want to examine?
et_str = 'pl'
etsamples = plsamples
etmsgs = plmsgs
etevents = plevents
# or
et_str = 'el'
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents


# have a look at time and gx
plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')


#%% Figure to examine which samples we exclude


plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')

plt.plot(etsamples.query('type=="blink"')['smpl_time'],etsamples.query('type=="blink"')['gx'],'o')
plt.plot(etsamples.query('type=="saccade"')['smpl_time'],etsamples.query('type=="saccade"')['gx'],'o')
plt.plot(etsamples.query('type=="fixation"')['smpl_time'],etsamples.query('type=="fixation"')['gx'],'o')
plt.legend(['sample','blink','saccade','fixation'])

plt.title(et_str)
plt.ylim([0,2500])

plt.plot(etsamples.query('neg_time==True')['smpl_time'],etsamples.query('neg_time==True')['gx'],'o')
plt.plot(etsamples.query('outside==True')['smpl_time'],etsamples.query('outside==True')['gx'],'o')
plt.plot(etsamples.query('zero_pa==True')['smpl_time'],etsamples.query('zero_pa==True')['gx'],'o')


#%%

#%%

#%%

#%%

#%%


#%%  EVENTS

#############  PL
plevents = events.pl_make_events(cleaned_plsamples)

# or
plblinkevents = events.pl_make_blink_events(cleaned_plsamples)
plsaccades = events.detect_saccades_engbert_mergenthaler(cleaned_plsamples,fs=240)



#############  EL
elevents = events.el_make_events(subject)

# have a look at how many saccades, blinks, fixations
plt.figure()
elevents['type'].value_counts().plot(kind='bar')

plt.figure()
elsacc = elevents.query('type=="saccade"')
elsacc['duration'] = (elsacc['end'] - elsacc['start'])
#elsacc.duration.round(3).value_counts().plot(kind='bar')



# Saccades from Engbert
elsaccades = events.detect_saccades_engbert_mergenthaler(orig_elsamples)

plt.figure()
plt.hist(elsacc.duration,bins=np.linspace(0,0.4,100),fc=(0, 1, 0, 0.5))
plt.hist(elsaccades.expanded_duration,bins=np.linspace(0,0.4,100),fc=(0, 0, 1, 0.5))
plt.hist(elsaccades.raw_duration,bins=np.linspace(0,0.4,100),fc=(1, 0, 0, 0.5))
plt.legend(['engbert','eyelink'])
# Sieht ziemlich anders aus?!?!




#%% EPOCHED

# epoch etdata according to query
condquery = 'condition == "DILATION" & exp_event=="lum"'
plepochs = df.make_epochs(plsamples, plmsgs.query(condquery))
elepochs = df.make_epochs(elsamples, elmsgs.query(condquery))


#%% PUPIL DILATION

# Looking at dilation data

elepochs.lum.unique()

# EL
etplot.plot_diam(elepochs,query='condition=="DILATION" & block==1 & lum==255')

# PL
etplot.plot_diam(plepochs, query='condition=="DILATION" & block==1 & lum==64')

etplot.plotTraces(plepochs, y='pa', query='condition=="DILATION" & lum==64')
etplot.plotTraces(elepochs, y='pa', query='condition=="DILATION" & block==1 & lum==255')


#%%

def plot_timeseries(etsamples,etsaccades,etsaccades2):

    print('plotting')
    plt.figure()
    plt.plot(etsamples.smpl_time, etsamples.gx, 'o')
    plt.plot(etsamples.query('type=="saccade"')['smpl_time'], etsamples.query('type=="saccade"')['gx'], 'o')
    plt.plot(etsamples.query('type=="blink"')['smpl_time'], etsamples.query('type=="blink"')['gx'], 'o')
    
    plt.plot(etsamples.smpl_time, etsamples.gy, 'o')
    plt.plot(etsamples.query('type=="saccade"')['smpl_time'], etsamples.query('type=="saccade"')['gy'], 'o')
    plt.plot(etsamples.query('type=="blink"')['smpl_time'], etsamples.query('type=="blink"')['gy'], 'o')

plot_timeseries(elsamples[0:-700000],elsaccades,elsacc)


#%%

# Plot Blinks PL

plt.plot(plsamples.smpl_time, plsamples.confidence, 'o')
plt.plot(plsamples.query('type=="blink"')['smpl_time'], plsamples.query('type=="blink"')['confidence']+0.01, 'o')
plt.plot(plsamples['smpl_time'], plsamples['blink_id'], 'o')



#%%

    
#    if len(np.intersect1d(etmsgs.columns,etevents.columns)) is not 0:
#        raise Exception('Some fields of etmsgs are already defined in etevents')
#            
#    for col in etmsgs.columns:
#        etevents[col] = pd.cut(etevents[timefield],[etmsgs.msg_time],labels=etmsgs.loc[1:-1,col])
#  

#%%

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


