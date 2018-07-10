#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 13:23:55 2018

@author: behinger
"""

import functions.add_path

import sys
sys.path
import functions.init_logger as init_logger
import logging
import functions.et_helper as  helper

import os
import time

import functions.et_preprocess as preprocess
from functions.detect_events import make_blinks,make_saccades,make_fixations


# loop over the foldernames (subjectnames)
# restricted to subjects that we do not exclude from analysis
# also loop over the et
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
logfilepath = '/net/store/nbp/projects/etcomp/log_files/'
rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP21', 'VP7']
# rejected_subjects =  ['pilot', '007', 'log_files', 'surface', 'VP1', 'VP2', 'VP3', 'VP4', 'VP7', 'VP8', 'VP11', 'VP12', 'VP14', 'VP15', 'VP20', 'VP23', 'VP24', 'VP25', 'VP26']
# ['pilot', '007', 'log_files', 'surface', 'VP1', 'VP7', 'VP8', 'VP11', 'VP12', 'VP14', 'VP15']
# rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP1', 'VP2', 'VP3', 'VP4', 'VP7', 'VP8', 'VP11', 'VP12', 'VP14']

# subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
subjectnames = ['VP14', 'VP20']
    
if 1 == 0:
    import subprocess 
    subprocess.check_output(["qsub",'-cwd','-N','etcomp2','-t','%i:%i'%(1,len(subjectnames)),'-l','mem=20G,h=!ramsauer.ikw.uni-osnabrueck.de','-e',logfilepath,'-o',logfilepath,'grid_preprocess.sge'])
    


print(os.environ['SGE_TASK_ID'])
subid = int(os.environ['SGE_TASK_ID'])-1
print(subid)
subject = subjectnames[subid] #jobID ranges from 1:N not 0:N-1
# change the loggerpath

init_logger.update_logger_filepath(newpath = os.path.join(logfilepath, 'log_preprocess_%s_subject%s.log'%(time.strftime("%Y_%m_%d-%H-%M-%S"),subject)))

logger = logging.getLogger(__name__)
ets               = ['pl', 'el']    
# preprocess for all subjects

for et in ets:
        logger.critical(' ')
        logger.critical('Eyetracker: %s    Subject: %s ', et, subject)
        etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))
