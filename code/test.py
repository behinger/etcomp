#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 20:27:34 2018

@author: behinger
"""
# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd

from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import os
import matplotlib.pyplot as plt
import functions.nbp_pupilhelper as nbp_pl
from pyedfread import edf
import functions.pl_recalib as pl

#%%
datapath = '/net/store/nbp/projects/etcomp/pilot'
subject = 'inga'


filename = os.path.join(datapath,subject,'raw')

pldata = pl_file_methods.load_object(os.path.join(filename,'pupil_data'))
#%%
pupil = pldata
# resort the timestamps
print('Sorting pupil_positions')
tIdx = [p['timestamp'] for p in pupil['pupil_positions']]
sortIndex = np.argsort(tIdx)
pupil['pupil_positions'] = [pupil['pupil_positions'][i] for i in sortIndex.tolist()]

calib_data = [note for note in pupil['notifications'] if 'subject' in note.keys() and note['subject'] == 'calibration.calibration_data']
calib_data = calib_data[0] # XXX fix this

print('Calculating Recalibration Function')
recalib_data= pl.pl_recalibV2(calib_data['pupil_list'],calib_data['ref_list'],pupil['pupil_positions'],detection_mode='2d')

