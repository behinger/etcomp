# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd

from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import os
import matplotlib.pyplot as plt
import functions.nbp_pupilhelper as nbp_pl
from pyedfread import edf

from functions import nbp_recalib

#%%
datapath = '/net/store/nbp/projects/etcomp/pilot'
subject = 'bene'


filename = os.path.join(datapath,subject,'raw')


pldata = pl_file_methods.load_object(os.path.join(filename,'pupil_data'))

def plot_trace(pupil,pos=0):
    t = [p['timestamp'] for p in pupil]
    x = [p['norm_pos'][pos] for p in pupil]
    plt.plot(t,x,'o')


    
#plot_trace(pldata['gaze_positions'])
#plot_trace(pldata['gaze_positions'],pos=1)
#plot_trace(pldata['gaze_positions2'])
#plot_trace(pldata['gaze_positions3'])

#plt.figure()
#plot_trace([p for p in pldata['pupil_positions'] if p['id'] == 0])

#plot_trace([p for p in pldata['pupil_positions'] if p['id'] == 1])

# recalibration 
pldata['gaze_positions'] = nbp_recalib.nbp_recalib(pldata)
#%%
def parse_message(msg):
    
    #print(msg)
    try:
        time = msg['time']
        string = msg['trialid '] # space on purpose
        
    except:
        try:
            time = msg['timestamp']
            string = msg['label']
        except:
                return(np.nan)
    
    split = string.split(' ')    
    parsedmsg = pd.DataFrame()
    if split[0] == 'GRID' and split[1] == 'element':
        parsedmsg = dict(
              time = time,  
              id=int(split[2]),
             posx = float(split[4]),
             posy = float(split[6]),
             total = int(split[8]),
             block = int(split[10])
                )
    return(pd.Series(parsedmsg))
    
    
    
def match_data(et,msgs,td=2):
    # Input: et(DataFrame) input data of the eyetracker
    #        msgs(DataFrame) already parsed input messages e.g. 'GRID element 5 pos-x 123 ...' defining experimental events
    # Output: Data.frame for each notification, find all samples that are in the range of +- td (default 2 s)
    pd_matched_data = pd.DataFrame()
    for idx,msg in msgs.iterrows():
        print(idx)
        ix = abs(et['time'] - msg['time'])<td # ix is a boolean (0 / 1, false / true)
        tmp= et.loc[ix]
        tmp = tmp.assign(td=tmp.time-msg['time'])
    
        
        msg_tmp = pd.concat([msg.to_frame()]*tmp.shape[0],axis=1).T
        msg_tmp.index = tmp.index
        
        
        tmp = pd.concat([tmp,msg_tmp],axis=1)
        pd_matched_data = pd_matched_data.append(tmp)
    return(pd_matched_data)
    
def findFile(path,ftype):
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out)

def plotTraces(et,query = 'posx == 960',figure = True):
    from bokeh.plotting import figure,show
    from bokeh.models import Span, CrosshairTool, HoverTool, ResetTool, PanTool, WheelZoomTool
    TOOLS = [CrosshairTool(dimensions='both'),
             HoverTool(),PanTool(),
             ResetTool()]
    if type(et) != list:
        et = [et]
    p = figure()
    for ix,e in enumerate(et):
        et[ix] = e.query(query) 
        et[ix] = et[ix][['gx','td','group']]
        et[ix]['group'] = ix
        
        
    tmp = pd.concat(et,ignore_index=True,)
     #   if figure:
            #plt.figure()

    p = figure(width=800,tools=TOOLS)
    p.circle(x=tmp.td,y=tmp.gx,color=tmp.group)
    show(p)        
    
    

#%%    

gridnotes = [note for note in pldata['notifications'] if 'label' in note.keys() and 'GRID' in note['label']]

pd_plmsgs = pd.DataFrame();
for note in gridnotes:
    msg = parse_message(note)
    if not msg.empty:
        pd_plmsgs = pd_plmsgs.append(msg, ignore_index=True)


pd_pldata = nbp_pl.gaze_to_pandas(pldata['gaze_positions'])

pd_pl_matched_data = match_data(pd_pldata,pd_plmsgs)

#%%


    

#%%
elsamples, elevents,elnotes = edf.pread(os.path.join(filename,findFile(filename,'.EDF')[0]), trial_marker=b'')
# change to seconds to be the same as pupil
elsamples['time'] = elsamples['time']/1000
elnotes['time'] = elnotes['trialid_time']/1000
elnotes = elnotes.drop('trialid_time',axis=1)
elevents['time'] = elevents['time']/1000

# if more than 90% of samples are on the the left, assume everything was recorded left
elsamples['gx']  = elsamples.gx_left if np.mean(elsamples.gx_left != -32768)>0.9 else elsamples.gx_right

#
pd_elmsgs = elnotes.apply(parse_message,axis=1)
pd_elmsgs = pd_elmsgs.dropna()
pd_el_matched_data = match_data(elsamples,pd_elmsgs)
#%%
pd_pl_matched_data.gx = pd_pl_matched_data.gx*1920
pd_pl_matched_data.gy = pd_pl_matched_data.gy*1280
#%%

plt.figure()
plotTraces([pd_pl_matched_data,pd_el_matched_data],query = 'posx==960',figure=False)

plt.figure()
plotTraces([pd_pl_matched_data,pd_el_matched_data],query = 'id == 15 & block == 1',figure=False)
    


#%%

pl2 = pd_pl_matched_data.copy()
pl2['td'] = pl2['td']-0.15 #for Katha pilot 0.02 (absolute diff in clock was 50ms in ~450seconds)
#pl2['gx'] = pl2['gx']
#%%
el2 = pd_el_matched_data[abs(pd_el_matched_data['gx'])<2500]
el2['gx'] = (el2['gx']/1920 - 0.5) * 0.5 + 0.42
#%%
plt.figure()

plotTraces([pl2,el2],query = 'block == 1& total==49 & id ==1',figure=False)
plt.figure()
plotTraces([pl2,el2],query = 'block == 1& total==13 & id ==13',figure=False)
plt.figure()
plotTraces([pl2,el2],query = 'block == 2& total==49 & id ==49',figure=False)



#%% ---- Have a look at the surface CSV files
# In the end they look super bad, the eyes are not fused properly.
surfacepath = os.path.join(filename,'exports','000','surfaces')
surface_files = [os.path.join(surfacepath,f) for f in findFile(surfacepath,'.csv')]

#pd.read_csv(os.path.join(file,surface_files[1])) # surface_gaze_distribution how many samples on surface, completely usesless
#pd.read_csv(os.path.join(file,surface_files[2])) # surface_events surface enter/exit, completly usesless for us


pd.read_csv(os.path.join(filename,surface_files[3])) #srf_positons_unnamed <- could be usefule for intrinsic camera undistortion
pldata_surface = pd.read_csv(os.path.join(filename,surface_files[4])) #gaze_positions_on_surface_unnamed <- thats the meat

plt.figure
plt.plot(pldata_surface['gaze_timestamp'],pldata_surface['x_norm'])

plt.figure
plt.plot(pldata_surface['x_norm'],pldata_surface['y_norm'],'o')


