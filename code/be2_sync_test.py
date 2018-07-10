#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 16:32:16 2018

@author: behinger
"""

import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import functions.et_plotting as etplot
import functions.et_preprocess as preprocess
import functions.et_make_df as make_df
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.pl_detect_blinks as pl_blinks

import functions.detect_bad_samples as detect_bad_samples

from functions.detect_events import make_blinks,make_saccades,make_fixations

from functions.et_make_df import make_epochs

from plotnine import *
#%%

# load and preprocess et data

# specify subject
subject = 'VP2'

# load pl data

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)

elsamples = detect_bad_samples.remove_bad_samples(elsamples)
plsamples = detect_bad_samples.remove_bad_samples(plsamples)
#%%
# THIS IS DANGEROUS BECAUSE I CHANGE THE TIMESTAMPS ONLY IN THE SAMPLES! NOT THE EVENTS
elsamples.smpl_time = elsamples.smpl_time - min(elsamples.smpl_time)
plsamples.smpl_time = plsamples.smpl_time - min(plsamples.smpl_time)
etsamples = pd.concat([elsamples.assign(eyetracker='eyelink'),plsamples.assign(eyetracker='pupillabs')],ignore_index=True, sort=False)


#%%
ggplot(etsamples,aes(x='smpl_time',y='gx',color='type',shape='eyetracker')) + geom_point()
#%%
condquery = 'condition == "DILATION" & exp_event=="lum"'
td = [-1, 15]
elepochs_pa = make_epochs(elsamples,elmsgs.query(condquery), td=td)
plepochs_pa = make_epochs(plsamples,plmsgs.query(condquery), td=td)



#normalize by SD division. Could be made better e.g. by quantile division
elepochs_pa['pa_norm'] = elepochs_pa.pa/np.std(elepochs_pa.pa)
plepochs_pa['pa_norm'] = plepochs_pa.pa/np.std(plepochs_pa.pa)

# Concatenate for easy ggplotting
etepochs_pa = pd.concat([elepochs_pa.assign(eyetracker='eyelink'),plepochs_pa.assign(eyetracker='pupillabs')],ignore_index=True)

# every 10th sample is enough
ggplot(etepochs_pa.query('lum>0').iloc[::10, :],aes(x='td',y='pa_norm',color='lum'))+\
            geom_point() +\
            geom_vline(xintercept=[0,3,10] )+\
            facet_wrap('~eyetracker') 


#%%
            
condquery = 'condition == "SMOOTH" & exp_event=="trialstart"'
td = [-0.2, 1]
elepochs_smooth = make_epochs(elsamples,elmsgs.query(condquery), td=td)
plepochs_smooth = make_epochs(plsamples,plmsgs.query(condquery), td=td)


# Concatenate for easy ggplotting
etepochs_smooth = pd.concat([elepochs_smooth.assign(eyetracker='eyelink'),plepochs_smooth.assign(eyetracker='pupillabs')],ignore_index=True)

# every 10th sample is enough
ggplot(etepochs_smooth,aes(x='td',y='gx',color='angle'))+\
            geom_point() +\
            geom_vline(xintercept=[0,0.2]) +\
            facet_wrap('~eyetracker') # split up by 
            

#%%
condquery = 'condition == "FREEVIEW" & exp_event=="trial"'
td = [-0.2, 6]
elepochs_fv = make_epochs(elsamples,elmsgs.query(condquery), td=td)
plepochs_fv= make_epochs(plsamples,plmsgs.query(condquery), td=td)


# Concatenate for easy ggplotting
etepochs_fv = pd.concat([elepochs_fv.assign(eyetracker='eyelink'),plepochs_fv.assign(eyetracker='pupillabs')],ignore_index=True)

# every 10th sample is enough
ggplot(etepochs_fv,aes(x='gx',y='gy'))+\
            geom_bin2d() +\
            geom_point(color='white') +\
            facet_wrap('~eyetracker') # split up by 
            
#%% An example to plot fixation durations in comparison
etevents= pd.concat([elevents.assign(eyetracker='eyelink'),plevents.assign(eyetracker='pupillabs')],ignore_index=True)
            
#Fixduration
ggplot(etevents.query('type=="fixation"'),aes(x='duration',color='eyetracker'))+geom_density()+xlim([0,1]) + ggtitle('Fixduration')

#Saccadeparameters
ggplot(etevents.query('type=="saccade"'),aes(x='amplitude',color='eyetracker'))+geom_density() + xlab('amplitude [px]') + ggtitle('Saccadeparameters')

# main sequence
# install scikit-misc
ggplot(etevents.query('type=="saccade"'),aes(x='np.log10(peak_velocity)',y='np.log10(amplitude)',color='eyetracker'))+stat_smooth(method='loess') + ggtitle('main sequence')
