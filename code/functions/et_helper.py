#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import os
import numpy as np

def gaze_to_pandas(gaze):
        # Input: gaze data as dictionary
        # Output: pandas dataframe with gx, gy, confidence, smpl_time pupillabsdata, diameter and (calculated) pupil area (pa)
        import pandas as pd
        
        list_diam= []
        list_pa= []
        for idx,p in enumerate(gaze):
            
            if p:
               if 'surface' in gaze[0]['topic']:
                    # we have a surface mapped dictionairy. We have to get the real base_data
                    # the schachtelung is: surfacemapped => base_data World Mapped => base_data pupil
                    p_basedata = p['base_data']['base_data']
               else:
                    p_basedata = p['base_data']


               # take the mean over all pupil-diameters
               diam = 0
               pa = 0
               for idx_bd,bd in enumerate(p_basedata):
                   pa = convert_diam_to_pa(bd['ellipse']['axes'][0], bd['ellipse']['axes'][1])
                   diam = diam + bd['diameter']
               diam = diam/(idx_bd+1)

               list_diam.append(diam)
               list_pa.append(pa)

                 
                
        df = pd.DataFrame({'gx':[p['norm_pos'][0] for p in gaze if p],
                           'gy':[p['norm_pos'][1] for p in gaze if p],
                           'confidence': [p['confidence'] for p in gaze if p],
                           'smpl_time':[p['timestamp'] for p in gaze if p],
                           'diameter':list_diam,
                           'pa': list_pa
                           })
        return(df)
        
        
def convert_diam_to_pa(axes1, axes2):
    return math.pi * float(axes1) * float(axes2) * 0.25
    
   
        
                
def add_events_to_samples(etsamples, etevents):

    
    
    for evt in etevents.type.unique():
        etsamples = append_eventtype_to_sample(etsamples,etevents,eventtype=evt)
        
        if evt== 'blink':
            # counts up the blink_id
            # Pure Magic
            etsamples['blink_id'] = (1*(etsamples['type']=='blink')) * ((1*(etsamples['type']=='blink')).diff()==1).cumsum()
    
    return(etsamples)
        
        
    ####################################
    # ADD BLINKS
    
       # detect Blink Samples
    # use blink column in elevents to mark all samples that are recorded during blink
    # filter all rows where blink==True
def append_eventtype_to_sample(etsamples,etevents,eventtype,timemargin=None):
    print('appending eventtype:',eventtype,' to samples')
    if timemargin is None:
        print('Taking Default value for timemargin (fix/saccade = 0s, blink = -0.1s/0.1s))')
        if eventtype== 'blink':
            timemargin = [-.1,.1]
        else:
            timemargin = [0,0]
        
               
    ix_event = etevents['type']==eventtype
    
    k = 0;
    for bindex,brow in etevents.loc[ix_event].iterrows():        
        if k%100==0:
            print('adding event',k,'from',np.sum(ix_event),'to etsamples')
        
        # get index of all samples that are +- timemargin ms of a detected event
        ix =  (etsamples.smpl_time>=(brow['start_time']+float(timemargin[0]))) & (etsamples.smpl_time<(brow['end_time']+float(timemargin[1])))
        
        if eventtype not in 'blink':        
            blinkSamplesInSaccade = etsamples.loc[ix,'type']=='blink'
            if np.any(blinkSamplesInSaccade):
                print(np.sum(blinkSamplesInSaccade),'blink samples detected in event')
            
        etsamples.loc[ix, 'type'] = eventtype
        k +=1
    return(etsamples)
                
    
def findFile(path,ftype):
    # finds file for el edf
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out)


 
        
