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


# Only por pupil labs!


def pupil_detect_blinks(plsamples):
    # Input:           pupillabs sample dataframe 
    # Output:          two columns df (is_blink, blink_id) with same index as samples
    
    print('Detecting blinks for pupillabs ...')
    
    # we will call the confidence level of pupillabs 'activity'
    activity = plsamples.confidence
    
    # total time
    total_time = plsamples.smpl_time.iloc[-1] - plsamples.smpl_time.iloc[1]
    
    # create filter
    windowsize = 0.2 # windowsize in second 
    
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
    
    # TODO specify
    onsets = filter_response > 0.1
    offsets = filter_response < -0.1
    
    # TODO
    response_classification = np.zeros(filter_response.shape)
    response_classification[onsets] = 1.
    response_classification[offsets] = -1.
            
    # TODO
    state = 'no blink'
    pd_blinks = np.empty(response_classification.shape[0])
    pd_blinks[:] = np.nan
    blink_id = 0
    
    # TODO
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
    
    # create pandas df               
    df_blink = pd.DataFrame()
    df_blink['is_blink'] = ~np.isnan(pd_blinks)*1
    df_blink.loc[df_blink['is_blink'] == True, 'type'] = "blink"
    
    # add blink columns to plsamples df 
    df_blink.index = plsamples.index
    plsamples_blink = pd.concat([plsamples, df_blink], axis=1)
    #df_blink['blink_id'] = pd_blinks
    
    
    blinkOnsets  = np.where(plsamples_blink.is_blink.diff() == 1)[0]
    blinkOffsets = np.where(plsamples_blink.is_blink.diff() == -1)[0]
    
    for startIdx,endIdx in zip(blinkOnsets,blinkOffsets):
        starttime = plsamples_blink.iloc[startIdx].smpl_time 
        endtime   = plsamples_blink.iloc[endIdx].smpl_time 

        ix = (plsamples_blink.smpl_time >= (starttime-0.1)) & (plsamples_blink.smpl_time < (endtime +0.1))
        plsamples_blink.loc[ix,'is_blink'] = 1
        
    # TODO documentation        
    plsamples_blink['blink_id'] = (plsamples_blink['is_blink'] * (plsamples_blink['is_blink'].diff()==1).cumsum())  
    
    
    print('Done ... detecting blinks for pupillabs ...')    

    return plsamples_blink