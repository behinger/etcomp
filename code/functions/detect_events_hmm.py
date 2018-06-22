# -*- coding: utf-8 -*-



import functions.add_path
import nslr_hmm

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.make_df as df
import functions.et_helper as  helper
import functions.et_plotting as etplot
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.et_preprocess as preprocess
import functions.pl_detect_blinks as pl_blinks
from functions.detect_events import make_blinks,make_saccades,make_fixations



#%%
#if 0:
#%%

subject = 'VP4'
etsamples, etmsgs, etevents = preprocess.preprocess_et('pl',subject,load=True)

#elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))
#%%
ix = range(1000)
t = etsamples.smpl_time.iloc[ix].values
eye = etsamples[['gx','gy']].iloc[ix].values
sample_class, segmentation, seg_class = nslr_hmm.classify_gaze(t, eye)

COLORS = {
        nslr_hmm.FIXATION: 'blue',
        nslr_hmm.SACCADE: 'black',
        nslr_hmm.SMOOTH_PURSUIT: 'green',
        nslr_hmm.PSO: 'yellow',
}

plt.plot(t, eye[:,0], '.')
for i, seg in enumerate(segmentation.segments):
    cls = seg_class[i]
    plt.plot(seg.t, np.array(seg.x)[:,0], color=COLORS[cls])

plt.show()
