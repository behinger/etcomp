# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
from lib.pupil.pupil_src.shared_modules import file_methods
import os
import matplotlib.pyplot as plt
import re
import functions.nbp_pupilhelper as nbp_pl
from pyedfread import edf


#%%
datapath = '/net/store/nbp/projects/etcomp/pilot'
subject = 'inga'

file = os.path.join(datapath,subject,'raw')


pldata = file_methods.load_object(os.path.join(file,'pupil_data'))

#%%
def parse_message(msg):
    
    print(msg)
    try:
        time = msg['time']
        string = msg['trialid ']
        
    except:
        time = msg['timestamp']
        string = msg['label']
    
    split = string.split(' ')    
    newnote = pd.DataFrame()
    if split[0] == 'GRID' and split[1] == 'element':
        newnote = dict(
              time = time,  
              id=int(split[2]),
             posx = float(split[4]),
             posy = float(split[6]),
             total = int(split[8]),
             block = int(split[10])
                )
    return(pd.Series(newnote))
    

gridnotes = [note for note in pldata['notifications'] if 'label' in note.keys() and 'GRID' in note['label']]
pd_newnotes = pd.DataFrame();
for note in gridnotes:
    newnote = parse_message(note)
    if not newnote.empty:
        pd_newnotes = pd_newnotes.append(newnote, ignore_index=True)


pd_pldata = nbp_pl.gaze_to_pandas(pldata['gaze_positions'])


def match_data(et,msgs):
    pd_matched_data = pd.DataFrame()
    for idx,msg in msgs.iterrows():
        print(idx)
        ix = abs(et['time'] - msg['time'])<1
        tmp= et.loc[ix]
        tmp = tmp.assign(td=tmp.time-msg['time'])
    
        
        note_tmp = pd.concat([msg.to_frame()]*tmp.shape[0],axis=1).T
        note_tmp.index = tmp.index
        
        
        tmp = pd.concat([tmp,note_tmp],axis=1)
        pd_matched_data = pd_matched_data.append(tmp)
    return(pd_matched_data)
    
pd_matched_data = match_data(pd_pldata,pd_newnotes)
tmp = pd_matched_data.query('posx == 960')
plt.figure()
plt.plot(tmp.td,tmp.x,'o')
    

p['label'] = 1

#%%
def findFile(path,ftype,returnN=1):
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out[0:(returnN)])
    

#%%
elsamples, elevents,elmessages = edf.pread(os.path.join(file,findFile(file,'.EDF')[0]), trial_marker=b'')
x = elmessages.apply(parse_message,axis=1)
x = x.dropna()
el_matched_data = match_data(elsamples,x)
#%%
elsamples, elevents,elmessages = edf.pread(os.path.join(file,findFile(file,'.EDF')[0]), filter='')

#%% look at triggers
pldata['notifications']



#%% ---- Have a look at the surface CSV files
# In the end they look super bad, the eyes are not fused properly.
surfacepath = os.path.join(file,'exports','000','surfaces')
surface_files = [os.path.join(surfacepath,f) for f in findFile(surfacepath,'.csv',returnN=-1)]

#pd.read_csv(os.path.join(file,surface_files[1])) # surface_gaze_distribution how many samples on surface, completely usesless
#pd.read_csv(os.path.join(file,surface_files[2])) # surface_events surface enter/exit, completly usesless for us


pd.read_csv(os.path.join(file,surface_files[3])) #srf_positons_unnamed <- could be usefule for intrinsic camera undistortion
pldata_surface = pd.read_csv(os.path.join(file,surface_files[4])) #gaze_positions_on_surface_unnamed <- thats the meat

plt.figure
plt.plot(pldata_surface['gaze_timestamp'],pldata_surface['x_norm'])

plt.figure
plt.plot(pldata_surface['x_norm'],pldata_surface['y_norm'],'o')


