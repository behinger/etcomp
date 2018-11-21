#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import os
import numpy as np
from numpy import pi,cos,sin

import pandas as pd

import logging

from plotnine import *


from scipy.stats.mstats import winsorize
from plotnine.stats.stat_summary import bootstrap_statistics


#%% put PUPIL LABS data into PANDAS DF

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
        return df
        
        
def convert_diam_to_pa(axes1, axes2):
    return math.pi * float(axes1) * float(axes2) * 0.25


#%% adding information to dfs

def add_msg_to_event(etevents,etmsgs,timefield = 'start_time', direction='backward'):
    # combine the event df with the msg df          
    etevents = etevents.sort_values('start_time')
    etmsgs   = etmsgs.sort_values('msg_time')
    # make a merge on the msg time and the start time of the events
    merged_etevents = pd.merge_asof(etevents,etmsgs,left_on='start_time',right_on='msg_time',direction=direction)
    
    return merged_etevents
    

                
def add_events_to_samples(etsamples, etevents):
    # Calls append_eventtype_to_sample for each event
    # Also adds blink_id
    logger = logging.getLogger(__name__)

    logger.info(etevents.type.unique())
    for evt in etevents.type.unique():
        etsamples = append_eventtype_to_sample(etsamples,etevents,eventtype=evt)
        
        # add blink id
        if evt == 'blink':
            # counts up the blink_id
            # Pure Magic
            etsamples.loc[:,'blink_id'] = (1*(etsamples['type']=='blink')) * ((1*(etsamples['type']=='blink')).diff()==1).cumsum()
    
    return(etsamples)
        
        
    
def append_eventtype_to_sample(etsamples,etevents,eventtype,timemargin=None):
    # get a logger
    logger = logging.getLogger(__name__)
     
    logger.debug('Appending eventtype: %s to samples',eventtype)
    if timemargin is None:
        
        if eventtype== 'blink':
            logger.info('Taking Default value for timemargin (blink = -0.1s/0.1s)')
            timemargin = [-.1,.1]
        else:
            logger.info('Taking Default value for timemargin (fix/saccade = 0s)')
            timemargin = [0,0]
        
               
    # get index of the rows that have that eventtype
    ix_event = etevents['type']==eventtype
    
    # get list of start and end indeces in the etsamples df
    eventstart = etevents.loc[ix_event,'start_time']+float(timemargin[0])
    eventend = etevents.loc[ix_event,'end_time']+float(timemargin[1])
    
    flat_ranges = eventtime_to_sampletime(etsamples,eventstart,eventend)
    # all etsamples with ix in ranges , will the eventype in the column type
    if len(flat_ranges) > 0:
        etsamples.loc[etsamples.index[flat_ranges], 'type'] = eventtype
        

    return etsamples

def eventtime_to_sampletime(etsamples,eventstart,eventend):
    # due to timemargin strange effects can occur and we need to clip
    mintime = etsamples.smpl_time.iloc[0]
    maxtime = etsamples.smpl_time.iloc[-1]
    eventstart.loc[eventstart < mintime] = mintime
    eventstart.loc[eventstart > maxtime] = maxtime
    eventend.loc[eventend  < mintime] = mintime
    eventend.loc[eventend  > maxtime] = maxtime
    
    if len(eventstart)!=len(eventend):
        raise error
        
    startix = np.searchsorted(etsamples.smpl_time,eventstart)
    endix = np.searchsorted(etsamples.smpl_time,eventend)
    
    
    #print('%i events of %s found'%(len(startix),eventtype))
    # make a list of ranges to have all indices in between the startix and endix
    ranges = [list(range(s,e)) for s,e in zip(startix,endix)]
    flat_ranges = [item for sublist in ranges for item in sublist]
    
    
    flat_ranges = np.intersect1d(flat_ranges,range(etsamples.shape[0]))
    return(flat_ranges)
#%% last fixation (e.g. for large GRID)

def only_last_fix(merged_etevents, next_stim = ['condition','block', 'element']):
    # we group by  block and element and then take the last fixation
    
    # TODO commented out cause it raises weird error
    # for HMM we define alle smooth pursuit as fixations
    # merged_etevents.type[merged_etevents.type == 'smoothpursuit'] = 'fixation'
    
    # use only fixation events and group by block and element and then take the last one of it
    large_grid_df = merged_etevents[merged_etevents.type == 'fixation'].groupby(next_stim).last()
    large_grid_df.reset_index(level= next_stim, inplace=True)

    return large_grid_df




#%% function to make groupby easier
    

def group_to_level_and_take_mean(raw_condition_df, lowestlevel):
    """
    make a groupby
    """
    
    if lowestlevel=='subject':
        # get df grouped by et and subject 
        # --> takes the mean of the accuracy and precision measures over all blocks
        grouped_df = raw_condition_df.groupby(['et', 'subject']).mean().reset_index(level=['et', 'subject'])
    
    
    elif lowestlevel=='block':
        # get df grouped by et, subject and block
        # --> makes a mean for each block of the subject
        grouped_df = raw_condition_df.groupby(['et', 'subject','block']).mean().reset_index(level=['et','subject','block'])


    elif lowestlevel=='element_positions':
        # get df grouped by et, subject and block
        # --> makes a mean for each block of the subject
        grouped_df = raw_condition_df.groupby(['et', 'subject', 'block','posx', 'posy']).mean().reset_index(level=['et', 'subject', 'block','posx', 'posy'])
         
        
    elif lowestlevel=='condition':
        # get df grouped by et, subject and GRID condition
        # --> makes a mean for each Gridcondition of the subject
        grouped_df = raw_condition_df.groupby(['et', 'subject', 'condition']).mean().reset_index(level=['et', 'subject', 'condition'])

        
    else:
        raise ValueError('This level is unknown / not implemented')
    
    return grouped_df


 


#%% set dtypes of dataframe and make the labes ready to get plotted
    
def set_dtypes(df):
    """
    Set the dtype of the categories, so that plotting is easier and more pretty.
    E.g. set column 'et' from object to categorical
    """        

    # make all object variables categorical
    df[df.select_dtypes(['object']).columns] = df.select_dtypes(['object']).apply(lambda x: x.astype('category'))
    
    # list of categorical variables that have to be treated separately as they were not object dtypes
    categorial_var = ["block", "trial", "pic_id"]
    
    # set columns to correct dtype
    for column in categorial_var:
        
        if column in df:
            # fill none values to not have problems with integers
            df[column] = df[column].fillna(-1)
            
            # convert ids to interger and round them to make them look nicely
            df[column] = pd.to_numeric(df[column], downcast='integer')            
            df[column] = df[column].round(0).astype(int)
            
            # convert -1 back to None
            df[column] = df[column].astype(str)
            df[column] = df[column].replace('-1', np.nan)
            
            # old version
            #df[column] = df[column].astype('category')
        
    
    # logging.debug('dtypes of the df after: %s', df.dtypes)    
    return df    


def set_to_full_names(df):
    """
    rename columns and values to their full name
    e.g. et --> Eye-Tracker
    """
    # TODO maybe more renaming?
    
    # maybe dont do this but rather use xaxis relabeling
    # rename columnnames
    # df = df.rename(index=str, columns={"et": "Eye-Tracker", "pic_id": "picture id", "fix_count": "number of fixations"})
    
    #rename values
    df.loc[:,'et'] = df['et'].map({'el': 'EyeLink', 'pl': 'Pupil Labs'})
    
    return df


#%% everything related to VISUAL DEGREES

def size_px2deg(px, mm_per_px=0.276,distance=600):
    """
    function to get the picture size of the freeviewing task
    from pixels into visual angle
    """
          
    deg = 2*np.arctan2(px/2*mm_per_px,distance)*180/np.pi

    return deg


def px2deg(px, orientation, mm_per_px=0.276,distance=600):
    # VD
    # "gx_px - gx_px-midpoint"
    # subtract center of our BENQ

    if orientation == 'horizontal':
        center_x = 1920 / 2
        px       = px - center_x
    
    elif orientation == 'vertical':
        center_y = 1080 / 2
        px       = px - center_y
    else:
        raise('unknown option')
    deg = np.arctan2(px*mm_per_px,distance)*180/np.pi

    return deg



def sph2cart(theta_sph,phi_sph,rho_sph=1):
    xyz_sph = np.asarray([rho_sph * sin(theta_sph) * cos(phi_sph), 
           rho_sph * sin(theta_sph) * sin(phi_sph), 
           rho_sph * cos(theta_sph)])

    return xyz_sph




#%% LOAD & SAVE & FIND file
    
def load_file(et,subject,datapath='/net/store/nbp/projects/etcomp/',outputprefix='',cleaned=True):
    
    # filepath for preprocessed folder
    preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
    et = outputprefix+et
    try:
        if cleaned:
            filename_samples = str(et)  + '_cleaned_samples.csv'
        else:
            filename_samples = str(et)  + '_samples.csv'
        filename_msgs    = str(et)  + '_msgs.csv'
        filename_events  = str(et)  + '_events.csv'
        
        etsamples = pd.read_csv(os.path.join(preprocessed_path,filename_samples))
        etmsgs    = pd.read_csv(os.path.join(preprocessed_path,filename_msgs))
        etevents  = pd.read_csv(os.path.join(preprocessed_path,filename_events))

    except FileNotFoundError as e:
        print(e)
        raise e

    return etsamples,etmsgs,etevents



def save_file(data,et,subject,datapath,outputprefix=''):
    
    # filepath for preprocessed folder
    preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
    
    # create new folder if there is none
    if not os.path.exists(preprocessed_path):
        os.makedirs(preprocessed_path)
    
    et = outputprefix+et
    # dump data in csv
    filename_samples = str(et) + '_samples.csv'
    filename_cleaned_samples = str(et) + '_cleaned_samples.csv'
    filename_msgs = str(et)  + '_msgs.csv'
    filename_events = str(et)  + '_events.csv'
    
    # make separate csv file for every df 
    data[0].to_csv(os.path.join(preprocessed_path, filename_samples), index=False)
    data[1].to_csv(os.path.join(preprocessed_path, filename_cleaned_samples), index=False)
    data[2].to_csv(os.path.join(preprocessed_path, filename_msgs), index=False)
    data[3].to_csv(os.path.join(preprocessed_path, filename_events), index=False)
    



def findFile(path,ftype):
    # finds file for el edf
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out)
    
    
    
def get_subjectnames(datapath='/net/store/nbp/projects/etcomp/'):
    return os.listdir(datapath)
   
    
#%% Tic Toc Matlab equivalent to time things
import time

def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator

# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds.\n" %tempTimeInterval )

def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)
    
    
    
    
def plot_around_event(etsamples,etmsgs,etevents,single_eventormsg,plusminus=(-1,1),bothET=True,plotevents=True):
    import re
    assert(type(single_eventormsg)==pd.Series)
    try:
        t0 = single_eventormsg.start_time
        eventtype = 'event'
    except:
        t0 = single_eventormsg.msg_time
        eventtype = 'msg'
    
    tstart = t0 + plusminus[0]
    tend = t0 + plusminus[1]
    query = '1==1'
    if ("subject" in etsamples.columns) & ("subject" in single_eventormsg.index):
        query = query+"& subject == @single_eventormsg.subject"
    if not bothET:
        query = query+"& eyetracker==@single_eventormsg.eyetracker"
    samples_query   = "smpl_time>=@tstart & smpl_time   <=@tend & "+query
    msg_query       = "msg_time >=@tstart & msg_time    <=@tend & "+query
    event_query     = "end_time >=@tstart & start_time  <=@tend & "+query
    etmsgs = etmsgs.query(msg_query)
    longstring = etmsgs.to_string(columns=['exp_event'],na_rep='',float_format='%.1f',index=False,header=False,col_space=0)
    longstring = re.sub(' +',' ',longstring)
    splitstring = longstring.split(sep="\n")
    if len(splitstring) == etmsgs.shape[0]-1:
        # last element was a Nan blank and got removed
        splitstring.append(' ')   
    etmsgs.loc[:,'label'] = splitstring

    p = (ggplot()
     + geom_point(aes(x='smpl_time',y='gx',color='type',shape='eyetracker'),data=etsamples.query(samples_query)) # samples
     + geom_text(aes(x='msg_time',y=2,label="label"),color='black',position=position_jitter(width=0),data=etmsgs)# label msg/trigger
     + geom_vline(aes(xintercept='msg_time'),color='black',data=etmsgs) # triggers/msgs
    )
         
    if etevents.query(event_query).shape[0]>0:
        pass
    if plotevents:
        p = p + geom_segment(aes(x="start_time",y=0,xend="end_time",yend=0,color='type'),alpha=0.5,size=2,data=etevents.query(event_query))
    if eventtype == 'event':
        p = (p   + annotate("line",x=[single_eventormsg.start_time,single_eventormsg.end_time],y=0,color='black')
                 + annotate("point",x=[single_eventormsg.start_time,single_eventormsg.end_time],y=0,color='black'))
    if eventtype=='msg':
        if single_eventormsg.condition == 'GRID':
            p = (p + annotate("text",x=single_eventormsg.end_time,y=single_eventormsg.posx+5,label=single_eventormsg.accuracy)
                   + geom_hline(yintercept=single_eventormsg.posx))
    return(p)
    
 
 


# define 20% winsorized means 

def winmean(x,perc = 0.2,axis=0):
    return(np.mean(winsorize(x,perc,axis=axis),axis=axis))

def winmean_cl_boot(series, n_samples=10000, confidence_interval=0.95,
                 random_state=None):
    return bootstrap_statistics(series, winmean,
                                n_samples=n_samples,
                                confidence_interval=confidence_interval,
                                random_state=random_state)

def mad(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    arr = np.ma.array(arr).compressed() # should be faster to not use masked arrays.
    med = np.median(arr)
    return np.median(np.abs(arr - med))
