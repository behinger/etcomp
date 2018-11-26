#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 13:23:55 2018

@author: behinger
"""

import functions.add_path

import sys,os
wd = os.getcwd()
sys.path
import functions.init_logger as init_logger
import logging
import functions.et_helper as  helper

import time

import functions.et_preprocess as preprocess
from functions.detect_events import make_blinks,make_saccades,make_fixations
from functions.detect_events_hmm import detect_events_hmm,detect_events_hmm_nosmooth    

os.chdir(wd)
# loop over the foldernames (subjectnames)
# restricted to subjects that we do not exclude from analysis
# also loop over the et
logfilepath = '/net/store/nbp/projects/etcomp/log_files/'

# loop over the foldernames (subjectnames)
# restricted to subjects that we do not exclude from analysis
# also loop over the et
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
#TODO find out whats wrong with vp3 and vp12 and fix and then use vp3 again!!
rejected_subjects = ['pilot', 'log_files', 'surface', 'results','007', 'VP8', 'VP21','VP7']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['el', 'pl']
#subjectnames = [subjectnames[i] for i in [9,14]]
#subjectnames = ['VP20']


ets=['pl']
#venv=> python3 grid_preprocess etcomp_hmm 

print(sys.argv)
if len(sys.argv)>1:
    job_name = sys.argv[1]
    assert(job_name in ['etcomp','etcomp_hmm','etcomp_hmm_nosmooth','etcomp_3d'])
    import subprocess 
    if len(sys.argv)>2:
        subprocess.check_output(["qsub",'-cwd','-N',job_name,'-t',sys.argv[2],'-l','mem=20G,h=!ramsauer.ikw.uni-osnabrueck.de','-e',logfilepath,'-o',logfilepath,'-q','nbp.q','grid_preprocess.sge'])
    else:
        subprocess.check_output(["qsub",'-cwd','-N',job_name,'-t','%i:%i'%(1,len(subjectnames)),'-l','mem=20G,h=!ramsauer.ikw.uni-osnabrueck.de','-e',logfilepath,'-o',logfilepath,'-q','nbp.q','grid_preprocess.sge'])
        
    
    sys.exit() 

job_name = os.environ['JOB_NAME']
print(os.environ['SGE_TASK_ID'])
subid = int(os.environ['SGE_TASK_ID'])-1

print(job_name)
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
        if job_name == 'etcomp':
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations ),outputprefix='')
        elif job_name == 'etcomp_3d':
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations ),outputprefix='3D',pupildetect='3d')
        elif job_name == 'etcomp_hmm':
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,detect_events_hmm),outputprefix='hmm_')
        elif job_name == 'etcomp_hmm_nosmooth':
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,detect_events_hmm_nosmooth),outputprefix='hmmnosmooth_')
        else:
            raise('Unknown jobname')
