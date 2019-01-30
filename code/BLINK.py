#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 18:20:44 2018

@author: behinger
"""

import functions.plotnine_theme
from plotnine import *
import numpy as np
from functions.et_helper import winmean,winmean_cl_boot

import MISC

#%%


def plot_duration(beep,option=''):
    
    beep['duration'] = beep.end_time - beep.start_time
    pl = ggplot(beep,aes(x="et",y="duration"))
    
    if option == '':
        pl = pl+\
        geom_jitter(width=0.2,height=0,alpha=0.8, color='lightblue')+\
        stat_summary(fun_data=winmean_cl_boot,data=beep.groupby(["subject","et"],as_index=False).agg({"duration":winmean}))+ggtitle('Median Blink Duration per block, subjectwise mean + subjectwise 95%CI')
    
    if option == 'facet_subjects':
        pl = ggplot(beep,aes(x="block",y="duration",fill="et",color="et"))+geom_point(position=position_dodge(width=0.2))+facet_wrap("~subject")
        
    pl = pl+expand_limits(y=0)

    
    MISC.print_results(beep, fields = ['duration'], agg_first_over_blocks=True, round_to=3)

    
    return pl   

    
#%%
def plot_count(beep,option=''):
    
    # add number of blinks
    beep = beep.groupby(["et","block","subject"]).size().reset_index(name='n_blinks')
    
    if option == '':
            pl = ggplot(beep,aes(x="et",y="n_blinks"))+\
        geom_jitter(width=0.2,height=0,alpha=0.8, color='lightblue')+\
                stat_summary(fun_data=winmean_cl_boot,data=beep.groupby(["subject","et"],as_index=False).agg({"n_blinks":winmean}))+ggtitle('Mean number of blinks per block, subjectwise mean + subjectwise 95%CI')
    
    if option == 'facet_subjects':
            pl = ggplot(beep,aes(x="block",y="n_blinks",color="et"))+\
                geom_jitter(position=position_dodge(width=0.2))+\
                facet_wrap("~subject")
    
    pl = pl+expand_limits(y=0)+scale_y_continuous(breaks=[1,3,5,7,9])
    
    # print stat results
    MISC.print_results(beep, fields = ['n_blinks'], agg_first_over_blocks=False, round_to=1)

    return pl   