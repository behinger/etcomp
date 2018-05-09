#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 17:06:02 2018

@author: pupil-labs/pupil
         https://github.com/pupil-labs/pupil/blob/0f4b329212c930346fb8e3b29440e08b7a27e7a3/pupil_src/shared_modules/blink_detection.py
"""
from scipy.signal import fftconvolve
import numpy as np
import pandas as pd

def pupil_detect_blinks(plsamples):
    activity = plsamples.confidence
    
    total_time = plsamples.smpl_time.iloc[-1] - plsamples.smpl_time.iloc[1]
    
    windowsize = 0.2# windowsize in second 
    
    filter_size = 2*int(round(plsamples.shape[0] * windowsize/ total_time/2))
    blink_filter = np.ones(filter_size) / filter_size
    
    # This is different from the online filter. Convolution will flip
    # the filter and result in a reverse filter response. Therefore
    # we set the first half of the filter to -1 instead of the second
    # half such that we get the expected result.
    blink_filter[:filter_size // 2] *= -1
    
    # The theoretical response maximum is +-0.5
    # Response of +-0.45 seems sufficient for a confidence of 1.
    filter_response = fftconvolve(activity, blink_filter, 'same') / 0.45
    
    onsets = filter_response > 0.1
    offsets = filter_response < -0.1
    
    response_classification = np.zeros(filter_response.shape)
    response_classification[onsets] = 1.
    response_classification[offsets] = -1.
            
    state = 'no blink'
    pd_blinks = np.empty(response_classification.shape[0])
    pd_blinks[:] = np.nan
    blink_id = 1
    for idx, classification in enumerate(response_classification):
                if state == 'no blink' and classification > 0:
                    state = 'blink started'
                    startidx = idx
                elif state == 'blink started' and classification == -1:
                    state = 'blink ending'
                    endidx = idx
                    
                elif state == 'blink ending' and classification >= 0:
                    # save blink
                    pd_blinks[int(filter_size/4+startidx):int(filter_size/4+endidx)] = blink_id
                    # add blink id
                    blink_id +=1
                    
                    if classification > 0:
                         state = 'blink started'
                         startidx = idx
                    else:
                        state = 'no blink'
                        
    output = pd.DataFrame()
    output['is_blink'] = ~np.isnan(pd_blinks)*1
    output['blink_id'] = pd_blinks
    
    return(output)