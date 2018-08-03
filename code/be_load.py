import functions.add_path


import functions.plotnine_theme
import pandas as pd
import numpy as np

import functions.et_preprocess as preprocess
import functions.et_helper as  helper





def load_data(algorithm='hmm_'):
    # loop over the foldernames (subjectnames)
    # restricted to subjects that we do not exclude from analysis
    # also loop over the et
    foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
    #TODO find out whats wrong with vp3 and vp12 and fix and then use vp3 again!!
    rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP21','VP7','all_preprocessed']
    subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
    #subjectnames = ['VP3']

    print('warning: removing DC offset of time-points (to semi align eyetrackers t=0)')
    datapath = '/net/store/nbp/projects/etcomp/'
    algorithm = ['hmm_']
    etsamples = pd.DataFrame()
    etmsgs= pd.DataFrame()
    etevents = pd.DataFrame()
    for subject in subjectnames:
        for et in ['el','pl']:
            for outputtype in algorithm:
                print('loading subject %s with et %s'%(subject,et))
                try:
                    elsamples, elmsgs, elevents = helper.load_file(et,subject,datapath=datapath,outputprefix=outputtype)
                except:
                    print('warning subject %s et %s not found'%(subject,et))
                    continue
                
                t0 = elmsgs.query("condition=='Instruction'&exp_event=='BEGINNING_start'").msg_time.values
                if len(t0)!=1:
                    raise error
                    
                elsamples.smpl_time = elsamples.smpl_time - t0
                elmsgs.msg_time= elmsgs.msg_time - t0
                elevents.start_time = elevents.start_time- t0
                elevents.end_time = elevents.end_time- t0

                if outputtype=='hmm_':
                    outputtype='hmm'

                etsamples = pd.concat([etsamples,elsamples.assign(subject=subject,eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
                etmsgs    = pd.concat([etmsgs,      elmsgs.assign(subject=subject,eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
                etevents  = pd.concat([etevents,  elevents.assign(subject=subject,eyetracker=et,algorithm=outputtype)],ignore_index=True, sort=False)
                
    return(etsamples,etmsgs,etevents)