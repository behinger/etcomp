import functions.add_path


import functions.plotnine_theme
import pandas as pd
import numpy as np

import functions.et_preprocess as preprocess
import functions.et_helper as  helper
import scipy
import scipy.stats

import logging





def load_data(algorithm='hmm_'):
    # loop over the foldernames (subjectnames)
    # restricted to subjects that we do not exclude from analysis
    # also loop over the et
    logger = logging.getLogger(__name__)
    foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')
    #TODO find out whats wrong with vp3 and vp12 and fix and then use vp3 again!!
    rejected_subjects = ['pilot', 'log_files', 'surface', '007', 'VP8', 'VP21','VP7','all_preprocessed']
    subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
    #subjectnames = ['VP3']

    logger.warning('warning: removing DC offset of time-points (to semi align eyetrackers t=0)')
    datapath = '/net/store/nbp/projects/etcomp/'
    algorithm = [algorithm]
    etsamples = pd.DataFrame()
    etmsgs= pd.DataFrame()
    etevents = pd.DataFrame()
    for subject in subjectnames:
        for et in ['el','pl']:
            for outputtype in algorithm:
                logger.info('loading subject %s with et %s'%(subject,et))
                try:
                    elsamples, elmsgs, elevents = helper.load_file(et,subject,datapath=datapath,outputprefix=outputtype)
                except:
                    logger.critical('warning subject %s et %s not found'%(subject,et))
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
    #regress pupillabs against eyelink, use triggers as identical timers

    for subject in etmsgs.subject.unique():
        logger.info("fixing subject %s"%(subject))
        etsamples,etmsgs,etevents = regress_eyetracker(etsamples,etevents,etmsgs,subject)
        
    return(etsamples,etmsgs,etevents)


  
def regress_eyetracker(etsamples,etevents,etmsgs,subject):
    ix_m = (etmsgs.eyetracker=='pl')&(etmsgs.subject==subject)
    ix_e = (etevents.eyetracker=='pl')&(etevents.subject==subject)
    ix_s = (etsamples.eyetracker=='pl')&(etsamples.subject==subject)
    
    
    # remove nans
    etmsgs_regress = etmsgs[etmsgs.exp_event.notnull()]
    # select the right ET & subject
    etmsgs_regress_el = etmsgs_regress.query("subject==@subject&eyetracker=='el'&condition!='Connect'")
    etmsgs_regress_pl = etmsgs_regress.query("subject==@subject&eyetracker=='pl'&condition!='Connect'")
    
    # remove the non common items
    

    remove_el = []
    remove_pl = []
    if subject=='VP4':
        remove_el = [874,874+713,474+874+713]
    if subject=='VP15':
        remove_el = [1878]
    if subject=='VP19':
                remove_el =[180] 
    if subject=='VP24':
        remove_el = [46,162]
        
    etmsgs_regress_el = etmsgs_regress_el[~etmsgs_regress_el.index.isin(etmsgs_regress_el.index[remove_el])]
    etmsgs_regress_pl = etmsgs_regress_pl[~etmsgs_regress_pl.index.isin(etmsgs_regress_el.index[remove_pl])]
    
    
    y = etmsgs_regress_el.msg_time.values
    x = etmsgs_regress_pl.msg_time.values
    assert(len(x)==len(y),'Error, there seems to be more or less messages in el than pl')
    slope,intercept,low,high = scipy.stats.theilslopes(y,x)
    
    print('slope:%.10f, intercept:%.10f'%(slope,intercept))
    #transform all pl timestamps
    etmsgs.loc[ix_m,'msg_time']     = etmsgs.loc[ix_m,'msg_time'].values     *slope + intercept
    etsamples.loc[ix_s,'smpl_time'] = etsamples.loc[ix_s,'smpl_time'].values *slope + intercept + 0.01 #this fixes the delay of PL camera to trigger (reported by pupillabs)
    etevents.loc[ix_e,'start_time'] = etevents.loc[ix_e,'start_time'].values *slope + intercept
    etevents.loc[ix_e,'end_time']   = etevents.loc[ix_e,'end_time'].values   *slope + intercept
    # we do not recalculate durations & velocity because the local change is so small (~0.1ms / 1s)
    
    return(etsamples,etmsgs,etevents)
