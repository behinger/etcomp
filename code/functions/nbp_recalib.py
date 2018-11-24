# -*- coding: utf-8 
"""
This code will recalibrate your PupilLabs data offline. 
Input:
    pupil lab data (3-key-dict of list of dicts)
    
Output:
    recalibrated gaze positions for monocular data (left and right eye) and
    binocular data (both eyes)
"""



import numpy as np
import functions.pl_recalib as pl



def nbp_recalib(pupil,calibration_mode='2d',eyeID=None):
    
    # resort the timestamps
    print('Sorting pupil_positions')
    pupil['pupil_positions'] = sort_pupil(pupil['pupil_positions'])
    
    calib_data = [note for note in pupil['notifications'] if 'subject' in note.keys() and note['subject'] == 'calibration.calibration_data']
    
    calib_data = sort_pupil(calib_data)
    recalib_data = []
    for calib_idx,single_calib in enumerate(calib_data):

        print('Calculating Recalibration Function')
        tstart = single_calib['pupil_list'][0]['timestamp']
        tend = single_calib['pupil_list'][-1]['timestamp']
        dur = tend - tstart
        print('Calibration started at t=%.2fs and stopped at t=%.2fs, duration=%.2fs'%(tstart,tend,dur))
        # get calib timestamps
        tsCalib = [p['timestamp'] for p in single_calib['pupil_list']] # not sure which timestamp to use..
        
        

        
        # get pupil timestamps
        tsPupil = np.array([p['timestamp'] for p in pupil['pupil_positions']])
        #tsGaze = np.array([p['timestamp'] for p in pupil['gaze_positions']])
        
        # get all samples after the latest sample of the current calibration
        idx = (tsPupil > np.max(tsCalib))
        if np.sum(idx) == 0:
            print('warning: no samples found after this calibration and before the next / the end')
            continue
        # in case there is a calibration afterwards, only calibrate up to the end of the calibration
        if calib_idx < len(calib_data)-1:
            next_calib = calib_data[calib_idx+1] 
            ts_nextCalib = [p['timestamp'] for p in next_calib['pupil_list']] # not sure which timestamp to use..
            idx = idx & (tsPupil < np.max(ts_nextCalib))
            print('recalibrating for %.2fs, %i samples'%(np.max(ts_nextCalib) - np.max(tsCalib),sum(idx)))
        else:
            print('recalibrating for %.2fs, %i samples'%(pupil['pupil_positions'][-1]['timestamp'] - np.max(tsCalib),sum(idx)))
            
        pupilPosition_cut =[pupil['pupil_positions'][i] for i in np.where(idx)[0].tolist()]
        print(len(single_calib))
        
        try:
            single_recalib_data = pl.pl_recalibV2(single_calib['pupil_list'],single_calib['ref_list'],pupilPosition_cut,calibration_mode=calibration_mode,eyeID = eyeID)        
        except:
            continue
                
        
        recalib_data = recalib_data + single_recalib_data
        
    return(recalib_data)
def sort_pupil(pupil):
    tIdx = [p['timestamp'] for p in pupil]
    sortIndex = np.argsort(tIdx)
    pupil = [pupil[i] for i in sortIndex.tolist()]
    return(pupil)