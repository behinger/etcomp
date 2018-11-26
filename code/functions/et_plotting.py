#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


#%%
# Plotting

def plot_trace(pupil):
    # Input: pupil is a list that contains a dictionary with 
    # Output: plot where the timestamp is on x-axis and the norm_pos is on the y-axis
    
    # collect all timestamps
    t = [p['timestamp'] for p in pupil]
    
    # horizontal component is at 'norm_pos'[0]; vertical at ['norm_pos'][1] respectively
    # could i call this norm_x? This is the position in pupillabs coordinates (0 <= x <= 1) world position?
    x = [p['norm_pos'][0] for p in pupil]
    # y = [p['norm_pos'][1] for p in pupil]
            
    plt.plot(t,x,'o')
    
    # plot x and y components (position on in world_camera_pic_norm)
    # plt.plot(x,y,'o')



def plotTraces(et,x='td',y = 'gx',query = '',showplot = True,width=1400,height=800):
    from bokeh.plotting import figure,show
    from bokeh.models import Span, CrosshairTool, HoverTool, ResetTool, PanTool, BoxZoomTool,WheelZoomTool
    from bokeh.transform import factor_cmap
    from bokeh.palettes import Spectral6


    TOOLS = [CrosshairTool(dimensions='both'),
             HoverTool(),PanTool(),BoxZoomTool(),
             ResetTool()]
    if type(et) != list:
        et = [et]
    p = figure()
    for ix,e in enumerate(et):
        #et[ix] = e.query(query) 
        et[ix]['group'] = str(ix)
        #et[ix] = et[ix][[field,'td','group']]

        
        
    tmp = pd.concat(et,ignore_index=True,)
    if len(query)>0:
        tmp = tmp.query(query)
     #   if figure:
            #plt.figure()
    if tmp.empty:
        raise 'Warning: No element left to plot'
    p = figure(width=width,tools=TOOLS,height=height)
    p.circle(x=x,y=y,source = tmp,legend='group',color=factor_cmap('group',factors=['0','1','2','3','4'], palette=Spectral6))
    if showplot:
        show(p)        
    return(p)
#%%
  

# calls the plot_trace function to make a plot where
# timestamp is on x-axis and the norm_pos[0] is on the y-axis
#plt.figure()
#plot_trace(original_pldata['gaze_positions'])

#plot_trace(original_pldata['gaze_positions2'])
#plot_trace(original_pldata['gaze_positions3'])


# left /right eye:  p['id'] == 0/1
# plot each eyes' pupil position in respect to pupilcamera_norm
#plt.figure()
#plot_trace([p for p in original_pldata['pupil_positions'] if p['id'] == 0])
#plot_trace([p for p in original_pldata['pupil_positions'] if p['id'] == 1])

#original_pldata['gaze_positions3'] = nbp_recalib.nbp_recalib(original_pldata,eyeID = 0)
    

#%%
# Looking at pupil dilation
    

def plot_diam(etepochs, query = 'condition=="DILATION" & block==1 & lum==64'):
    # Input:    etepochs  epoched etdata         
    #           query     all samples that fulfill query get selected
    #           measure   set to pa for el  or to diameter for pl
    # Output:   plot with x-axis: td time and y-axis: horiz. comp. of gaze

    # select relevant data    
    dilation_data_subset = etepochs.query(query).loc[:,['td', 'pa', 'lum', 'condition']]
    # print head of plottet df
    print(dilation_data_subset.head()) 

    plt.figure()
    plt.plot(dilation_data_subset['td'],dilation_data_subset['pa'], 'o')
    

