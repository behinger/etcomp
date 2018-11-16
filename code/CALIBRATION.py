#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 13:11:40 2018

@author: behinger
"""
import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


import functions.et_preprocess as preprocess


import functions.pl_surface as pl_surface
from functions import et_import
from lib.pupil.pupil_src.shared_modules import accuracy_visualizer
from functions.pl_recalib import pl_recalibV2

import logging

def find_closest_gridstart(elcaliberror,gridstart):
    # because we often recalibrate multiple times, we have to look for the most recent one. The most recent one of each block is the one, that is closest to the grid start trigger
    out = pd.DataFrame()
    for t in gridstart:
        minix = np.argmin(np.abs(t-elcaliberror.msg_time))
        out = pd.concat([out,elcaliberror.iloc[minix]],axis=1)
        
    return(out.T)

def el_accuracy(subject):
    samp,evt,elnotes = et_import.raw_el_data(subject, datapath='/net/store/nbp/projects/etcomp/')

    ix = elnotes["trialid "].str.find("!CAL VALIDATION HV13 ")
    elcaliberror = elnotes[ix==0]


    elcaliberror = elcaliberror.join(elcaliberror["trialid "].str.extract("ERROR ([\d.]*) avg. ([\d.]*)"))
    elcaliberror = elcaliberror.rename(columns={0:"avg",1:"max","trialid_time":"msg_time"})
    elcaliberror = elcaliberror.assign(subject=subject,eyetracker='el')
    elcaliberror.loc[:,'msg_time'] = elcaliberror.loc[:,'msg_time']/1000
    elcaliberror = elcaliberror.drop(axis=1,labels=["py_trial_marker","trialid "])
    elcaliberror = elcaliberror.reset_index()
    
    # get trialstart times
    gridstart = elnotes.loc[elnotes["trialid "].str.find("Instruction for LARGEGG start")==0,'trialid_time']/1000
    elcaliberror = find_closest_gridstart(elcaliberror,gridstart)
    
    return(elcaliberror)

def pl_accuracy(subject):
    logger = logging.getLogger(__name__)

    logger.info('loading subject %s'%(subject))
    pldata = et_import.raw_pl_data(subject=subject)
    
    # get calibration and accuracy data
    data = [n for n in pldata['notifications'] if n['subject'] in ['calibration.calibration_data','accuracy_test.data']]
    
    
    
    notes = [n['subject'] for n in data]
    # where are accuracy tests?
    ix_acc  = np.where(np.asarray(notes) == 'accuracy_test.data')[0]
    
    # give me the calibrations immediately before
    ix_cal = ix_acc-1
    
    # if calib test was started multiple times, remove them
    ix_cal = ix_cal[np.diff(np.append(-1,ix_acc))!=1]
    ix_acc = ix_acc[np.diff(np.append(ix_acc,-1))!=1]
    
    logger.info("found %i calibrations"%(ix_cal.shape))
    fake_gpool = pl_surface.fake_gpool_surface(folder='/net/store/nbp/projects/etcomp/%s/raw'%(subject))
    
    
    class fake_accuracy(accuracy_visualizer.Accuracy_Visualizer):
        def __init__(self):
            #self.outlier_threshold = 5
            self.succession_threshold = np.cos(np.deg2rad(.5))
            self._outlier_threshold = 5 
            

    combined = [(data[c],data[a]) for c,a in zip(ix_cal,ix_acc)]
    
    accu = []
    prec = []
    time = []
    #combined = combined[6:9]
    tmp = fake_accuracy()
    for cal,acc in combined:
        gaze_pos = pl_recalibV2(cal['pupil_list'],cal['ref_list'],acc['pupil_list'],calibration_mode='2d',eyeID=None)    
        
        results= tmp.calc_acc_prec_errlines(gaze_pos,acc['ref_list'],fake_gpool.capture.intrinsics)
        accu.append(results[0].result)
        prec.append(results[1].result)
        time.append(cal['pupil_list'][0]['timestamp'])
    
 
    plcaliberror = pd.DataFrame({"avg":accu,"msg_time":time,'subject':subject,'eyetracker':'pl'})
    
    
    
    # get trial start notifications
    # but some subject do not have accuracy messages (no idea why!!, pupil bug?)
    if plcaliberror.shape[0]>0:
        gridstart = [n['recent_frame_timestamp'] for n in pldata['notifications'] if 'label' in n.keys() and type(n['label']==str) and len(n['label'])>0 and n['label'].find("Instruction for LARGEGG start")==0]
        plcaliberror = find_closest_gridstart(plcaliberror,gridstart)
    
    return(plcaliberror)