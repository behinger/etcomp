#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 18:20:44 2018

@author: behinger
"""

import functions.plotnine_theme
from plotnine import *

#%%

def plot_duration(beep):
    beep['duration'] = beep.end_time - beep.start_time
    (
     ggplot(beep,aes(x="block",y="duration",color="et"))+
         geom_point(position=position_dodge(width=0.2))+
         expand_limits(y=0)
     ).draw()
#%%
def plot_count(beep):
    (
     ggplot(beep.groupby(["et","block","subject"]).size().reset_index(name='n_blinks'),aes(x="block",y="n_blinks",color="et"))+
         geom_point(position=position_dodge(width=0.2))+
         expand_limits(y=0)
     ).draw()