# -*- coding: utf-8 
"""
This code will recalibrate your PupilLabs data offline. 
Input:
    pupil lab data (3-key-dict of list of dicts)
    
Output:
    recalibrated gaze positions for monocular data (left and right eye) and
    binocular data (both eyes)
"""


#import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import functions.pl_recalib as pl
from imp import reload
#import file_methods


def nbp_recalib(pupil,calibration_mode='2d',eyeID=None):
    
    # resort the timestamps
    print('Sorting pupil_positions')
    tIdx = [p['timestamp'] for p in pupil['pupil_positions']]
    sortIndex = np.argsort(tIdx)
    pupil['pupil_positions'] = [pupil['pupil_positions'][i] for i in sortIndex.tolist()]
    
    calib_data = [note for note in pupil['notifications'] if 'subject' in note.keys() and note['subject'] == 'calibration.calibration_data']
    calib_data = calib_data[0] # XXX fix this
    
    print('Calculating Recalibration Function')
    #mapperBino = pl.pl_recalibV2(calib_data['pupil_list'],calib_data['ref_list'],pupil['gaze_positions'],detection_mode='2d')

    #map_fn_all= pl.get_map_fn(calib_data['pupil_list'],calib_data['ref_list'])
    
    
    
    tsCalib = [p['timestamp'] for p in calib_data['pupil_list']] # not sure which timestamp to use..
    
    tsPupil = np.array([p['timestamp'] for p in pupil['pupil_positions']])
    #tsGaze = np.array([p['timestamp'] for p in pupil['gaze_positions']])
    
    idx = (tsPupil > np.max(tsCalib))
    pupilPosition_cut =[pupil['pupil_positions'][i] for i in np.where(idx)[0].tolist()]
    
    recalib_data = pl.pl_recalibV2(calib_data['pupil_list'],calib_data['ref_list'],pupilPosition_cut,calibration_mode=calibration_mode,eyeID = eyeID)
    return(recalib_data)
  