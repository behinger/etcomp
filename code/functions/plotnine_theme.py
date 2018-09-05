#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 15:44:24 2018

@author: kgross

specify layout/themes of plots made with plotnine

"""

import functions.add_path

from plotnine import *
from plotnine.data import *


theme_set(theme_minimal(base_size=12) + theme(text = element_text(),\
               panel_background = element_rect(colour = 'None'),\
               plot_background = element_rect(colour = 'None'),\
               panel_border = element_rect(colour = 'None'),\
               axis_title = element_text(size = 10),\
               axis_title_y = element_text(angle=90,vjust =0),\
               # with va you can move xlab title matplotlibstyle
               axis_title_x = element_text(),\
               axis_text = element_text(),\
               axis_line = element_line(colour="black"),\
               axis_ticks = element_line(),\
               panel_grid_major = element_line(colour="#f0f0f0"),\
               panel_grid_minor = element_blank(),\
               legend_key = element_rect(colour = 'None'),\
               legend_position = "bottom",\
               legend_background=element_rect(fill='None',color='None'),\
               legend_direction = "horizontal",\
               legend_box = 'horizontal',\
               legend_margin = 10,\
               legend_title = element_text(size=10),\
               legend_title_align = 'left',\
               strip_background=element_rect(colour="#ffffff",fill="#ffffff"),\
               strip_text = element_text(face="bold")))
               
   