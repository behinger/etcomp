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
import functions.preprocess_et as preprocess
import functions.make_df as df
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.pl_detect_blinks as pl_blinks

import functions.detect_bad_samples as detect_bad_samples

from functions.detect_events import make_blinks,make_saccades,make_fixations

from functions.make_df import make_epochs

from plotnine import *
#%%

# load and preprocess et data

# specify subject
subject = 'VP1'

# load pl data

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)

elsamples = detect_bad_samples.remove_bad_samples(elsamples)
plsamples = detect_bad_samples.remove_bad_samples(plsamples)

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
            
