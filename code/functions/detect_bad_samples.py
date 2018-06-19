#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 19:01:13 2018

@author: kgross
"""
import pandas as pd
import numpy as np
import functions.et_helper as  helper

import logging


#%% Detect bad samples
    
def detect_bad_samples(etsamples):
    # adds columns for bad samples (out of monitor, sampling frequency)
    
    # get a logger
    logger = logging.getLogger(__name__)
     
    logger.info("Removing bad samples ...")
    
    # create df to store index of merked samples
    marked_samples = pd.DataFrame()
    
    # Gaze Position
    # is out of the range of the monitor
    # The monitor has a size of 1920 x 1080 pixels
    # we give tolerance of 500 px and we convert into visual degrees
    # VD 
    ix_outside_samples = (etsamples.gx < (helper.px2deg(-500, 'horizontal'))) | (etsamples.gx > (helper.px2deg(2420, 'horizontal'))) | (etsamples.gy < (helper.px2deg(-500, 'vertical'))) | (etsamples.gy > (helper.px2deg(1580, 'vertical')))
    percentage_outside = np.mean(ix_outside_samples)*100
    logger.warning("Caution: %.2f%% samples got marked as the calculated gazeposition is outside the monitor"%(percentage_outside))
    
    if (percentage_outside > 40):
        raise NameError('More than 40% of the data got marked because the gaze is outside the monitor.') 
    
    marked_samples['outside'] = ix_outside_samples
    
    
    # Sampling Frequency
    # check how many samples there are with a fs worse than 120 Hz
    tmp = pd.DataFrame()
    tmp['fs'] = etsamples.smpl_time.diff()
    ix_bad_freq = tmp.fs > (1./120.)
    percentage_bad_freq = np.mean(ix_bad_freq)*100
    logger.warning("Caution: %.2f%% samples have a sampling frequency worse than 120 Hz"%(percentage_bad_freq))
    
    
    # Pupil Area is NaN
    ix_zero_pa = np.isnan(etsamples.pa)
    percentage_zero_pa = np.mean(ix_zero_pa)*100
    logger.warning("Caution: %.2f%% samples got marked as the pupil area is NaN in the samples"%(percentage_zero_pa))
    marked_samples['zero_pa'] = ix_zero_pa
    

    # Negative sample time    
    ix_neg_time = (etsamples.smpl_time < 0)
    percentage_neg_time = np.mean(ix_neg_time)*100
    logger.warning("Caution: %.2f%% samples got marked as they have negative time stamps"%(percentage_neg_time))
    marked_samples['neg_time'] = ix_neg_time
    
    
    # concatenate bad sample column(s)
    marked_samples.index = etsamples.index
    annotated_samples = pd.concat([etsamples, marked_samples], axis=1)
    
    return annotated_samples


#%% Remove bad samples
    
def remove_bad_samples(marked_samples):
    # Input:      samples df that has coulmns that mark bad samples with 'True'
    # Output:     cleaned sample df where rows th
    
    # check if columns that mark bad samples exist
    assert('outside' in marked_samples)
    marked_samples = marked_samples[marked_samples['outside']==False]

    
    assert('type' in marked_samples)   
    marked_samples = marked_samples[~(marked_samples['type']=='blink')]

    assert('zero_pa' in marked_samples)    
    marked_samples = marked_samples[marked_samples['zero_pa']==False]

    assert('neg_time' in marked_samples)    
    marked_samples = marked_samples[marked_samples['neg_time']==False]

   
    return marked_samples




