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
subject = 'VP2'

# load pl data
plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=False,save=False,eventfunctions=(make_blinks,make_saccades,make_fixations))


# load el data
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=False,eventfunctions=(make_blinks,make_saccades,make_fixations))



#%% LOAD preprocessed DATA from csv file

plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)


import functions.detect_bad_samples as detect_bad_samples

#%% LOOK at GRID condition
# Only first block and only large Grid

etsamples = plsamples
etmsgs = plmsgs
etevents = plevents


# remove bad samples
clean_etsamples = detect_bad_samples.remove_bad_samples(etsamples)

# find out start and end  time of the large Grid condition
select = 'block == 1 & condition == "GRID" & grid_size == 49'
gridstart_time = etmsgs.query(select + '& element == 1').msg_time.values[0]
gridend_time = etmsgs.query(select + '& element == 49').msg_time.values[0]

# only focus on important columns and only consider samples that are labeled as fixations
ix_fix = (clean_etsamples.type == 'fixation') & ((clean_etsamples.smpl_time > gridstart_time) & (clean_etsamples.smpl_time < gridend_time))
reduced_clean_etsamples = clean_etsamples.loc[ix_fix,['gy', 'gx', 'smpl_time', 'type']]

# debugging
#plt.figure()
#plt.plot(clean_etsamples.smpl_time,clean_etsamples.gx,'o')
#
#plt.plot(gridend_time,750,'o')
#plt.plot(clean_etsamples.query('type=="fixation"').smpl_time, clean_etsamples.query('type=="fixation"').gx,'o')
#plt.plot(clean_etsamples.query('type=="saccade"').smpl_time, clean_etsamples.query('type=="saccade"').gx,'o')
#


#%% Plot
figure, axarr = plt.subplots(2, 2)

# Show stimulus Grid points
axarr[0, 0].set_title('Grid that was shown in block 1')
# get all gridpoints that were shown on the screen
x_grid_elements = etmsgs.query(select).groupby('element').first()['posx']
y_grid_elements = etmsgs.query(select).groupby('element').first()['posy']
axarr[0, 0].plot(x_grid_elements, y_grid_elements,'o')


# use all samples that are within 2 sec of a msg and that are labeled as fixations
axarr[0, 1].set_title('Gaze block 1 using all samples (only fixations)')
axarr[0, 1].plot(reduced_clean_etsamples.gx, reduced_clean_etsamples.gy,'o')
axarr[0, 1].plot(reduced_clean_etsamples.gx, reduced_clean_etsamples.gy,'o')


# plot the mean fixation positions of all fixations during the grid condition
axarr[1, 0].set_title('Gaze block 1 using events')

# get indices of event df that are within the time window and that are fixations
ix_grid_fix = ((etevents.start_time > gridstart_time) & (etevents.end_time < gridend_time)) & (etevents.type == 'fixation')

axarr[1, 0].plot(etevents.loc[ix_grid_fix, 'mean_gx'], etevents.loc[ix_grid_fix, 'mean_gy'],'o')


# plot the actual Grid and the recorded fixations in the same plot
axarr[1, 1].set_title('Overlaid plot')
axarr[1, 1].plot(x_grid_elements, y_grid_elements,'o')
axarr[1, 1].plot(etevents.loc[ix_grid_fix, 'mean_gx'], etevents.loc[ix_grid_fix, 'mean_gy'],'o')



#%% make a list of fixations between two stimuli

#block 2 elem 12 13 seltsamer mean
# and 13  14 


# find out msg time for element 1 in block 1 Large Grid
select = 'block == 2 & condition == "GRID" & grid_size == 49'
elem1_time = etmsgs.query(select + '& element == 12').msg_time.values[0]
elem2_time = etmsgs.query(select + '& element == 13').msg_time.values[0]
elem1_posx = etmsgs.query(select + '& element == 12').posx.values[0]
elem1_posy = etmsgs.query(select + '& element == 12').posy.values[0]

elem_before_posx = etmsgs.query(select + '& element == 11').posx.values[0]
elem_before_posy = etmsgs.query(select + '& element == 11').posy.values[0]


elem_after_posx = etmsgs.query(select + '& element == 13').posx.values[0]
elem_after_posy = etmsgs.query(select + '& element == 13').posy.values[0]


# look at event df and select all fixations in the time window
ix_fix = ((etevents.start_time > elem1_time) & (etevents.start_time <= elem2_time)) & (etevents.type == 'fixation')


# plot results
figure, axarr = plt.subplots(2, 2)

# Show stimulus Grid points
axarr[0, 0].set_title('Grid that was shown in block 1')
# get all gridpoints that were shown on the screen
x_grid_elements = etmsgs.query(select).groupby('element').first()['posx']
y_grid_elements = etmsgs.query(select).groupby('element').first()['posy']
axarr[0, 0].plot(x_grid_elements, y_grid_elements,'o')


# Show mean position of the fixations
axarr[1, 1].set_title('fixations')
axarr[1, 1].plot(x_grid_elements, y_grid_elements,'o')
axarr[1, 1].plot(elem_before_posx, elem_before_posy,'o')
axarr[1, 1].plot(elem1_posx, elem1_posy,'o')
axarr[1, 1].plot(elem_after_posx, elem_after_posy,'o')
axarr[1, 1].plot(etevents.loc[ix_fix, 'mean_gx'], etevents.loc[ix_fix, 'mean_gy'],'o')
# alle fixation samples reinplotten
axarr[1, 1].plot(etsamples.query('smpl_time>%.4f & smpl_time<%.4f & type=="fixation"'%(elem1_time,elem2_time)).gx, etsamples.query('smpl_time>%.4f & smpl_time<%.4f & type=="fixation"'%(elem1_time,elem2_time)).gy, 'o')# noch alle samples reinhauen
#und alle saccades
axarr[1, 1].plot(etsamples.query('smpl_time>%.4f & smpl_time<%.4f & type=="saccade"'%(elem1_time,elem2_time)).gx, etsamples.query('smpl_time>%.4f & smpl_time<%.4f & type=="saccade"'%(elem1_time,elem2_time)).gy, 'x') 




#%% trying to make it into the loop


select = 'block == 1 & condition == "GRID" & grid_size == 49'
elem1_time = etmsgs.query(select + '& element == 10').msg_time.values[0]
elem2_time = etmsgs.query(select + '& element == 11').msg_time.values[0]
elem1_posx = etmsgs.query(select + '& element == 10').posx.values[0]
elem1_posy = etmsgs.query(select + '& element == 10').posy.values[0]



# look at event df and select all fixations in the time window
ix_fix_events = ((etevents.start_time > elem1_time) & (etevents.end_time <= elem2_time)) & (etevents.type == 'fixation')

# get all samples that belong to the fixations
fix_samples = pd.DataFrame()

#for fix in range(sum(ix_fix_events)):
#    fix_samples['fix_no'] =  fix + 1
#    ix_fix_sample
#    fix_samples['gx'] = etsamples.loc[] fix + 1
#    
#

# plot results
figure, axarr = plt.subplots(2, 2)

# Show stimulus Grid points
axarr[0, 0].set_title('Grid that was shown in block 1')
# get all gridpoints that were shown on the screen
x_grid_elements = etmsgs.query(select).groupby('element').first()['posx']
y_grid_elements = etmsgs.query(select).groupby('element').first()['posy']
axarr[0, 0].plot(x_grid_elements, y_grid_elements,'o')


# Show mean position of the fixations
axarr[0, 0].set_title('mean position of the fixations')
axarr[1, 1].plot(x_grid_elements, y_grid_elements,'o')
axarr[1, 1].plot(elem1_posx, elem1_posy,'o')
axarr[1, 1].plot(elevents.loc[ix_fix_events, 'mean_gx'], elevents.loc[ix_fix_events, 'mean_gy'],'o')




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


