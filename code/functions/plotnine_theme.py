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




default_theme = (theme_minimal(base_size=12) + theme(text = element_text(),\
               panel_background = element_rect(colour = 'None'),\
               plot_background = element_rect(colour = 'None'),\
               
               # title position
               plot_title = element_text(va = 'center'),\
               panel_border = element_rect(colour = 'None'),\
               
               axis_title = element_text(size = 10),\

               # with va you can move xlab title matplotlibstyle
               axis_title_y = element_text(angle=90, vjust=0),\
               axis_title_x = element_text(),\
               
               # style of Koordinatenachsen und deren Beschriftungen
               axis_text = element_text(colour="black"),\
            
               axis_line = element_line(colour="black"),\
               axis_ticks = element_line(colour="black"),\

               axis_ticks_pad_minor=1,\
               
               # specify the backgroundgrid here
               # light grey grid:
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
               


# setting theme to default
theme_set(default_theme)



#%% saving different themes for different plots

# show large grid fixations (no grid in background)
display_fixation_theme = (theme_minimal(base_size=12) + theme(text = element_text(),\
               panel_background = element_rect(colour = 'None'),\
               plot_background = element_rect(colour = 'None'),\
               
               # title position
               plot_title = element_text(va = 'center'),\
               panel_border = element_rect(colour = 'None'),\
               
               axis_title = element_text(size = 10),\

               # with va you can move xlab title matplotlibstyle
               axis_title_y = element_text(angle=90, vjust=0),\
               axis_title_x = element_text(),\
               
               # style of Koordinatenachsen und deren Beschriftungen
               axis_text = element_text(colour="lightgrey"),\
               #axis_line = element_line(colour="black"),\               
               axis_line = element_line(colour="lightgrey"),\
               axis_ticks = element_line(colour="lightgrey"),\

               axis_ticks_pad_minor=1,\
               
               # specify the backgroundgrid here
               # no grid
               panel_grid_major=element_line(),\
               panel_grid_major_x=element_blank(),\
               panel_grid_major_y=element_blank(),\
               panel_grid_minor=element_line(),\
               panel_grid_minor_x=element_blank(),\
               panel_grid_minor_y=element_blank(),\
    
            
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



"""
Possibility to change position of the xlab title:
    
    # save old theme
    old_theme = theme_get()
    
    
    # TODO: check if there is a difference to theme_set(old_theme + theme(axis_title_x = element_text(va = "top")))
    theme_set(old_theme + theme(axis_title_x = element_text()))

    # restore old theme
    theme_set(old_theme)
    
    
    
And with this you can move the zahlen an der koordinatenachse further away from the axis
axis_text = element_text(margin={'t': 15, 'r': 15}),\

"""
