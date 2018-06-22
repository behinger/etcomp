# -*- coding: utf-8 -*-



import functions.add_path

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

from functions.et_helper import tic,toc




def detect_events_hmm(etsamples,etevents,et):
    
    #etevents = etevents.loc[etevents.start_time < etsamples.smpl_time.iloc[-1]]
    from functions.et_helper import append_eventtype_to_sample
    import nslr_hmm

    # First add blinks
    etsamples = append_eventtype_to_sample(etsamples,etevents,eventtype='blink')
    etsamples = etsamples.iloc[1:2000]
    #
    
    
    
    #etsamples = etsamples.iloc[1:1000]
    t = etsamples.query('type!="blink"').smpl_time.values
    eye = etsamples.query('type!="blink"')[['gx','gy']].values

    tic()
    sample_class, segmentation, seg_class = nslr_hmm.classify_gaze(t, eye,optimize_noise=False)
    toc()
    sample_class = sample_class.astype(int)
    if 1 == 0:    
        plt.figure()
        COLORS = {
                nslr_hmm.FIXATION: 'blue',
                nslr_hmm.SACCADE: 'black',
                nslr_hmm.SMOOTH_PURSUIT: 'green',
                nslr_hmm.PSO: 'yellow',
        }
        
        plt.plot(t, eye[:,0], '.')
        for i, seg in enumerate(segmentation.segments):
            cls = seg_class[i]
            plt.plot(seg.t, np.array(seg.x)[:,0], 'o-',color=COLORS[cls])
        
        plt.show()
        
    eventtypes = np.asarray(['fixation','saccade','smoothpursuit','pso'])
    nonblink = etsamples.type != 'blink'
    etsamples.loc[nonblink,'type'] = eventtypes[sample_class-1]
    etevents = pd.concat([etevents,
                         sampletype_to_event(etsamples,'saccade'),
                         sampletype_to_event(etsamples,'smoothpursuit'),
                         sampletype_to_event(etsamples,'pso'),
                         sampletype_to_event(etsamples,'fixation')],ignore_index=True)
    
    
    return(etsamples,etevents)
    
def sampletype_to_event(etsamples,eventtype):

   
    # use magic to get start and end times of fixations in a temporary column
    etsamples['tmp'] = (1*(etsamples['type'] == eventtype)).diff()
    # assume that we always start with a fixation
    
    etsamples.iloc[0, etsamples.columns.get_loc('tmp')] = 1
    etsamples['tmp'] = etsamples['tmp'].astype(int)
        
    # make a list of the start and end times
    start_times_list = list(etsamples.loc[etsamples['tmp'] == 1, 'smpl_time'].astype(float))
    end_times_list   = list(etsamples.loc[etsamples['tmp'] == -1, 'smpl_time'].astype(float))
    
    # drop the temporary column
    
    # add them as columns to a fixationevent df
    events = pd.DataFrame([start_times_list, end_times_list], ['start_time', 'end_time']).T

    # delete event if start or end is NaN
    events.dropna(subset=['start_time', 'end_time'], inplace=True)

    # add the type    
    events['type'] = eventtype
    events['duration'] = events['end_time'] - events['start_time']
    #events['start_gx'] =  list(etsamples.loc[etsamples['tmp'] == 1,  'gx'].astype(float))
    #events['start_gy'] =  list(etsamples.loc[etsamples['tmp'] == 1,  'gy'].astype(float))
    #events['end_gx']   =  list(etsamples.loc[etsamples['tmp'] == -1, 'gx'].astype(float))
    #events['end_gy']   =  list(etsamples.loc[etsamples['tmp'] == -1, 'gy'].astype(float))
    

    for ix,row in events.iterrows():
        # take the mean gx/gy position over all samples that belong to that fixation
        # removed bad samples explicitly
        ix = (etsamples.smpl_time >= row.start_time) & (etsamples.smpl_time <= row.end_time)
#        events.loc[ix, 'mean_gx'] =  np.mean(etsamples.loc[ix, 'gx'])    
#        events.loc[ix, 'mean_gy'] =  np.mean(etsamples.loc[ix, 'gy'])
        

        
        #if fix_samples.empty:
        #    logger.error('Empty fixation sample df encountered for fix_event at index %s', ix)

        #else:                
            # the thetas are the difference in spherical angle
         #   fixdf = pd.DataFrame({'x0':etsamples.iloc[:-1].gx.values,'y0':etsamples.iloc[:-1].gy.values,'x1':etsamples.iloc[1:].gx.values,'y1':etsamples.iloc[1:].gy.values})
         #   thetas = fixdf.apply(lambda row:make_df.calc_3d_angle_points(row.x0,row.y0,row.x1,row.y1),axis=1)
       
            # calculate the rms 
      #      events.loc[ix, 'spher_rms'] = np.sqrt(((np.square(thetas)).mean()))
            
    # cleanup
    etsamples.drop('tmp', axis=1, inplace=True)
    return(events)
#if 1 == 0:
subject = 'VP4'
etsamples, etmsgs, etevents = preprocess.preprocess_et('el',subject,load=False,save=True,outputprefix='hmm_',eventfunctions=(make_blinks,detect_events_hmm))
    