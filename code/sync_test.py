# -*- coding: utf-8 -*-

import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import functions.et_plotting as etplot
import functions.preprocess as preprocess
import functions.make_df as df
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.pl_detect_blinks as pl_blinks


#%%
# load and preprocess et data

# specify subject
subject = 'inga_3'

#############  PL
# load pl data
# original_pldata = load.raw_pl_data(subject)

# preprocess pl_pldata to get 2 dataframes: samples, msgs
plsamples, plmsgs = preprocess.preprocess_pl(subject, date='2018-05-18', recalculate=True,save=False)
plsamples.type.unique()


#############  EL
# load **preprocessed** el data as 2 dataframes: samples msgs
elsamples, elmsgs = preprocess.preprocess_el(subject, date='2018-05-18', recalculate=True,save=False)




#%% BAD SAMPLES

# remove bad_samples (gaze outside monitor, bad frequency)
orig_elsamples = preprocess.mark_bad_samples(elsamples)

####events = make_events
####orig_elsamples= add_sacc_fix_labels(orig_elsamples,events)


cleaned_elsamples = preprocess.remove_bad_samples(orig_elsamples)



####return cleaned_elsamples,elevents,elmsgs

# TODO look at this sample and think if this is possible
orig_elsamples.iloc[918689, :]



# remove bad_samples (gaze outside monitor, bad frequency)
orig_plsamples = preprocess.mark_bad_samples(plsamples)
cleaned_plsamples = preprocess.remove_bad_samples(orig_plsamples)



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

plot_timeseries(elsamples[0:-700000],elsaccades,elsacc)


elsaccades.head()
elsaccades.columns
elsaccades.describe()


#%%

# Plot Blinks PL

plt.plot(plsamples.smpl_time, plsamples.confidence, 'o')
plt.plot(plsamples.query('is_blink==1')['smpl_time'], plsamples.query('is_blink==1')['confidence']+0.01, 'o')
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


