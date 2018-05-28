# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import functions.et_plotting as etplot
import functions.preprocess_et as preprocess
import functions.make_df as df
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.pl_detect_blinks as pl_blinks

from functions.detect_events import make_blinks,make_saccades,make_fixations




#%% LOAD DATA and preprocess RAW data


# specify subject
subject = 'VP1'

# load pl data
plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))


# load el data
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=False,eventfunctions=(make_blinks,make_saccades,make_fixations))



#%% LOAD preprocessed DATA from csv file

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)

#%%  

#%% Figure to examine which samples we exclude

from functions.detect_bad_samples import detect_bad_samples,remove_bad_samples
etsamples_orig = elsamples
etsamples_clean = remove_bad_samples(etsamples_orig)
etsamples = etsamples_clean
    


plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')

plt.plot(etsamples.query('type=="blink"')['smpl_time'],etsamples.query('type=="blink"')['gx'],'o')
plt.plot(etsamples.query('type=="saccade"')['smpl_time'],etsamples.query('type=="saccade"')['gx'],'o')
plt.plot(etsamples.query('type=="fixation"')['smpl_time'],etsamples.query('type=="fixation"')['gx'],'o')



plt.plot(etsamples.query('neg_time==True')['smpl_time'],etsamples.query('neg_time==True')['gx'],'o')
plt.plot(etsamples.query('outside==True')['smpl_time'],etsamples.query('outside==True')['gx'],'o')
plt.plot(etsamples.query('zero_pa==True')['smpl_time'],etsamples.query('zero_pa==True')['gx'],'o')

#%%  EVENTS

#############  PL
plevents = events.pl_make_events(cleaned_plsamples)

# or
plblinkevents = events.pl_make_blink_events(cleaned_plsamples)
plsaccades = events.detect_saccades_engbert_mergenthaler(cleaned_plsamples,fs=240)



#############  EL
elevents = events.el_make_events(subject)

# have a look at how many saccades, blinks, fixations
plt.figure()
elevents['type'].value_counts().plot(kind='bar')

plt.figure()
elsacc = elevents.query('type=="saccade"')
elsacc['duration'] = (elsacc['end'] - elsacc['start'])
#elsacc.duration.round(3).value_counts().plot(kind='bar')



# Saccades from Engbert
elsaccades = events.detect_saccades_engbert_mergenthaler(orig_elsamples)

plt.figure()
plt.hist(elsacc.duration,bins=np.linspace(0,0.4,100),fc=(0, 1, 0, 0.5))
plt.hist(elsaccades.expanded_duration,bins=np.linspace(0,0.4,100),fc=(0, 0, 1, 0.5))
plt.hist(elsaccades.raw_duration,bins=np.linspace(0,0.4,100),fc=(1, 0, 0, 0.5))
plt.legend(['engbert','eyelink'])
# Sieht ziemlich anders aus?!?!




#%% EPOCHED

# epoch etdata according to query
condquery = 'condition == "DILATION" & exp_event=="lum"'
plepochs = df.make_epochs(plsamples, plmsgs.query(condquery))
elepochs = df.make_epochs(elsamples, elmsgs.query(condquery))


#%%

# We are going to have 5 types of Dataframes:
# sample, msgs, events, epochs und for each condition a df FULL for pl and el respectively 
# for more details please have a look at the "overview dataframes pdf"



#%% PUPIL DILATION

# Looking at dilation data

elepochs.lum.unique()


# TODO something is still wrong with dilation

# EL
etplot.plot_diam(elepochs,query='condition=="DILATION" & block==1 & lum==255')

# PL
etplot.plot_diam(plepochs, query='condition=="DILATION" & block==1 & lum==64')



etplot.plotTraces(plepochs, y='pa', query='condition=="DILATION" & lum==64')
etplot.plotTraces(elepochs, y='pa', query='condition=="DILATION" & block==1 & lum==255')


#%%

# Detect Saccades

plsaccades = saccades.detect_saccades_engbert_mergenthaler(cleaned_plsamples,fs=240)
elsaccades = saccades.detect_saccades_engbert_mergenthaler(cleaned_elsamples)



def plot_timeseries(etsamples,etsaccades,etsaccades2):

    print('plotting')
    plt.figure()
    plt.plot(etsamples.smpl_time, etsamples.gx, 'o')
    plt.plot(etsamples.query('type=="saccade"')['smpl_time'], etsamples.query('type=="saccade"')['gx'], 'o')
    plt.plot(etsamples.query('type=="blink"')['smpl_time'], etsamples.query('type=="blink"')['gx'], 'o')
    
    plt.plot(etsamples.smpl_time, etsamples.gy, 'o')
    plt.plot(etsamples.query('type=="saccade"')['smpl_time'], etsamples.query('type=="saccade"')['gy'], 'o')
    plt.plot(etsamples.query('type=="blink"')['smpl_time'], etsamples.query('type=="blink"')['gy'], 'o')

plot_timeseries(elsamples[0:-700000],elsaccades,elsacc)


elsaccades.head()
elsaccades.columns
elsaccades.describe()


#%%

# Plot Blinks PL

plt.plot(plsamples.smpl_time, plsamples.confidence, 'o')
plt.plot(plsamples.query('type=="blink"')['smpl_time'], plsamples.query('type=="blink"')['confidence']+0.01, 'o')
plt.plot(plsamples['smpl_time'], plsamples['blink_id'], 'o')



#%%

#%%

#%%   

# Plotting

# plot pl against el
# if fixationcross presented at posx==960
# x-axis: td time 
# y-axis: horiz. component of gaze 
etplot.plotTraces([plepochs,elepochs],query = 'posx==960')

etplot.plotTraces([plepochs,elepochs],query = 'element == 15 & block == 1',figure=False)


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


