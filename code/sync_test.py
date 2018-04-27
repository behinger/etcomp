# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
import os,sys,inspect

from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import os
import matplotlib.pyplot as plt
import functions.nbp_pupilhelper as nbp_pl
import functions.etcomp_parse as parse

# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib

#%%
# set path and subjectname
datapath = '/net/store/nbp/projects/etcomp/pilot'
subject = 'inga'

filename = os.path.join(datapath,subject,'raw')

# load pupillabs data (dictionary)
# with dict_keys(['notifications', 'pupil_positions', 'gaze_positions'])
# where each value is a list that contains a dictionary
pldata = pl_file_methods.load_object(os.path.join(filename,'pupil_data'))

# 'notification'
# dict_keys(['record', 'subject', 'timestamp', 'label', 'duration'])

# 'pupil_positions'
# dict_keys(['diameter', 'confidence', 'method', 'norm_pos', 'timestamp', 'id', 'topic', 'ellipse'])

# 'gaze_positions'
# dict_keys(['base_data', 'timestamp', 'topic', 'confidence', 'norm_pos'])

# where 'base_data' has a dict within a list 
# dict_keys(['diameter', 'confidence', 'method', 'norm_pos', 'timestamp', 'id', 'topic', 'ellipse'])

# where 'normpos' is a list (with horizon. and vert. component)


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



# calls the plot_trace function to make a plot where
# timestamp is on x-axis and the norm_pos[0] is on the y-axis
#plt.figure()
#plot_trace(pldata['gaze_positions'])

#plot_trace(pldata['gaze_positions2'])
#plot_trace(pldata['gaze_positions3'])


# left /right eye:  p['id'] == 0/1
# plot each eyes' pupil position in respect to pupilcamera_norm
#plt.figure()
#plot_trace([p for p in pldata['pupil_positions'] if p['id'] == 0])
#plot_trace([p for p in pldata['pupil_positions'] if p['id'] == 1])

#pldata['gaze_positions3'] = nbp_recalib.nbp_recalib(pldata,eyeID = 0)
    
#%%
 
def match_data(et,msgs,td=2):
    # Input: et(DataFrame) input data of the eyetracker (has column smpl_time)
    #        msgs(DataFrame) already parsed input messages e.g. 'GRID element 5 pos-x 123 ...' defining experimental events (has column msg_time)
    # Output: Data.frame for each notification, find all samples that are in the range of +-td (default timediff 2 s)
    pd_matched_data = pd.DataFrame()
    
    for idx,msg in msgs.iterrows():
        print(idx)
        ix = abs(et['smpl_time'] - msg['msg_time'])<td # ix is a boolean (0 / 1, false / true) (this way we find all samples +-td)
        if np.sum(ix) == 0:
            print('warning, no sample found for msg %i'%(idx))
            print(msg)
            continue
        tmp= et.loc[ix]
        tmp = tmp.assign(td=tmp.smpl_time-msg['msg_time'])
    
        
        msg_tmp = pd.concat([msg.to_frame()]*tmp.shape[0],axis=1).T
        msg_tmp.index = tmp.index
        
        
        tmp = pd.concat([tmp,msg_tmp],axis=1)
        pd_matched_data = pd_matched_data.append(tmp)
   
    return(pd_matched_data)
    
  
    
def findFile(path,ftype):
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out)


def plotTraces(et,query = 'posx == 960',figure = True):
    # Input:    et         
    #           query     all samples that fulfill query get selected
    #           figure
    # Output:   plot with x-axis: td time and y-axis: horiz. comp. of gaze
    if type(et) != list:
        et = [et]
    for dat in et:
        tmp = dat.query(query)
        if figure:
            plt.figure()
        plt.plot(tmp.td,tmp.gx,'o')
    

#%%
        
# make a list of gridnotes that contain all notifications of pldata if they contain 'label'
gridnotes = [note for note in pldata['notifications'] if 'label' in note.keys()]

# pandas df that contains all pl parsed messages
pd_plmsgs = pd.DataFrame();
for note in gridnotes:
    msg = parse.parse_message(note)
    if not msg.empty:
        pd_plmsgs = pd_plmsgs.append(msg, ignore_index=True)

# inspect msgs df
pd_plmsgs.columns


# use pupilhelper func to make samples df (confidence, gx, gy, smpl_time) and sort according to smpl_time
pd_pldata = nbp_pl.gaze_to_pandas(pldata['gaze_positions'])
pd_pldata.sort_values('smpl_time',inplace=True)

# match the et data to the msgs (match smpl_time to msg_time)
pd_pl_matched_data = match_data(pd_pldata,pd_plmsgs)


# print(pd_pl_matched_data.query('condition=="SMOOTH"'))
#%%

# Get and parse EL data
# elsamples:  contains individual EL samples
# elevents:   contains fixation and saccade definitions
# elnotes:    contains notes (meta data) associated with each trial
elsamples, elevents, elnotes = edf.pread(os.path.join(filename,findFile(filename,'.EDF')[0]), trial_marker=b'')

# change to seconds to be the same as pupil
elsamples['smpl_time'] = elsamples['time']/1000

elnotes['msg_time'] = elnotes['trialid_time']/1000
elnotes = elnotes.drop('trialid_time',axis=1)

elevents['msg_time'] = elevents['time']/1000

# determine recorded eye
# if more than 90% of samples are on the the left, assume everything was recorded left
elsamples['gx']  = elsamples.gx_left if np.mean(elsamples.gx_left != -32768)>0.9 else elsamples.gx_right
elsamples['gy']  = elsamples.gy_left if np.mean(elsamples.gy_left != -32768)>0.9 else elsamples.gy_right

# parse EL msg and match data to get pandas df
pd_elmsgs = elnotes.apply(parse.parse_message,axis=1)
pd_elmsgs = pd_elmsgs.drop(pd_elmsgs.index[pd_elmsgs.isnull().all(1)])

# match the et data to the msgs (match smpl_time to msg_time)
pd_el_matched_data = match_data(elsamples,pd_elmsgs)



#%%

# We are going to have 5 types of Dataframes: sample, msgs, events, epochs und for each condition a df FULL for pl and el respectively 


# Inspection of resulting df

# confidence:    pupillabs (sub-pixel estimation of contour): ratio (detected/perfect)
# gx/gy:         horiz./vert. gaze in world camera
# smpl_time:     pl/el timestamp of sample
# td:            timedifference (default=2)
# block:         specifies block of recording
# cond:          name of condition
# msg_time:      time when msg was sent
# trial:         number of trial
# calib_ET:      was it the calibration phase of ET? (boolean)
# element:       id of gridpoint (element)
# posx/posy:     position of presented fixation point (ground truth) in pix on screen?
# total:         49=large Grid ; 13=calibration Grid
# pic_id         id of the presented picture
# start          ?was it start??
# stop           ?was it stop??
# beep           number of beep
# lum            luminance


print(pd_pl_matched_data.dtypes)
print(pd_el_matched_data)



# trying to plot a little
# fixationcross vert. posy at 540  (middle of screen)  and in td btw. 0 and 0.4
example = pd_el_matched_data.query('posy==540&td>0.18 & td<0.5')       # for EL
# example = pd_pl_matched_data.query('posy==540&td>0 & td<0.4')     # for PL
print(example.head())
print(example.columns)

plt.figure()
plt.plot((example['gx'] ),(example['gy'] ),'o')          # gaze



#%%

pd_pl_matched_data.gx = pd_pl_matched_data.gx*1920

#%%
# plot pl against el   if fixationcross presented at posx==960
# x-axis: td time 
# y-axis: horiz. component of gaze 
plotTraces([pd_pl_matched_data,pd_el_matched_data],query = 'posx==960')

plotTraces([pd_pl_matched_data,pd_el_matched_data],query = 'element == 15 & block == 1',figure=False)
    





#%% ---- Have a look at the surface CSV files
# In the end they look super bad, the eyes are not fused properly.
surfacepath = os.path.join(filename,'exports','000','surfaces')
surface_files = [os.path.join(surfacepath,f) for f in findFile(surfacepath,'.csv',returnN=-1)]

#pd.read_csv(os.path.join(file,surface_files[1])) # surface_gaze_distribution how many samples on surface, completely usesless
#pd.read_csv(os.path.join(file,surface_files[2])) # surface_events surface enter/exit, completly usesless for us


pd.read_csv(os.path.join(file,surface_files[3])) #srf_positons_unnamed <- could be usefule for intrinsic camera undistortion
pldata_surface = pd.read_csv(os.path.join(file,surface_files[4])) #gaze_positions_on_surface_unnamed <- thats the meat

plt.figure
plt.plot(pldata_surface['gaze_timestamp'],pldata_surface['x_norm'])

plt.figure
plt.plot(pldata_surface['x_norm'],pldata_surface['y_norm'],'o')


