#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 12 13:58:59 2018

@author:   kgross
"""





#%% convert df table into latex pdf and png

"""
import pandas as pd
import numpy as np
import subprocess

filename = 'out.tex'
pdffile = 'out.pdf'
outname = 'out.png'

template = r'''\documentclass[preview]{{standalone}}
\usepackage{{booktabs}}
\begin{{document}}
{}
\end{{document}}
'''

with open(filename, 'wb') as f:
    f.write(bytes(template.format(df.to_latex()),'UTF-8'))

subprocess.call(['pdflatex', filename])
subprocess.call(['convert', '-density', '300', pdffile, '-quality', '90', outname])
"""







                        # caution that limiting the axis, does not cut off fixations from plot
                        coord_cartesian(xlim=(-37.0,37.0), ylim=(-16.0,16.0)) +

#%% investigate on the position of fixations (use density)

# only for sanity:
# plotting all fixations for each eye tracker
ggplot(complete_freeview_df, aes(x='mean_gx', y='mean_gy')) \
        + geom_point(aes(size = 'duration', color = 'pic_id')) \
        + guides(color=guide_legend(ncol=40)) \
        + facet_grid('.~et') \
        + ggtitle('EyeLink vs PupilLabs: All fixations of all subjects of all trials')


# looking at density distributions
# for each gaze component (horizontal/vertical) and for each eyetracker
gaze_comp_freeview_df = freeview_df.melt(id_vars=['et', 'subject', 'block', 'trial', 'pic_id', 'start_time', 'end_time', 'duration', 'rms'], var_name='gaze_comp')

# display both eye tracker in the same plot
ggplot(gaze_comp_freeview_df, aes(x='value', color = 'et')) \
       + stat_density(geom='line', kernel='gaussian') \
       + xlab('Position in visual angle (degrees)') \
       + facet_grid('.~gaze_comp')


# using a 2D visualization for the density
ggplot(freeview_df, aes(x='mean_gx', y='mean_gy')) \
    + stat_density_2d() \
    + facet_grid('.~et') \
    + ggtitle('EyeLink vs PupilLabs: Density distribution over all subjects and all trials')







# JUST FOR ME
ggplot(freeview_df, aes(x='mean_gx', y='mean_gy')) \
    + geom_point(alpha = 0.25, color='red') \
    + stat_density_2d() \
    + facet_grid('.~et') \
    + ggtitle('EyeLink vs PupilLabs: Density distribution over all subjects and all trials')




#%% All the old ANALYSIS get condition df functions:


#%% Create large_grid_df for all subjects


def get_complete_large_grid_df(subjectnames, ets,**kwargs):
    # make the df for the large GRID for both eyetrackers and all subjects
    
    # create df
    complete_large_grid_df = pd.DataFrame()
        
    for subject in subjectnames:
        for et in ets:
            logging.critical('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=True,**kwargs)
            
            # adding the messages to the event df
            merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time', direction='backward')
                       
            # make df for grid condition that only contains ONE fixation per element
            # (the last fixation before the new element  (used a groupby.last() to achieve that))
            large_grid_df = make_df.make_large_grid_df(merged_events)          
            
            # add a column for eyetracker and subject
            large_grid_df['et'] = et
            large_grid_df['subject'] = subject
            
            # concatenate to the complete df
            complete_large_grid_df = pd.concat([complete_large_grid_df,large_grid_df])
                   
    return complete_large_grid_df




#%% Create small_large_grid_df for all subjects


def get_complete_small_large_grid_df(subjectnames, ets,**kwargs):
    # make the df for all elements that appear in the small AND the large GRID for both eyetrackers and all subjects
    
    # create df
    complete_small_large_grid_df = pd.DataFrame()
        
    for subject in subjectnames:
        for et in ets:
            logging.critical('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=True,**kwargs)
            
            # adding the messages to the event df
            merged_events = helper.add_msg_to_event(etevents, etmsgs, timefield = 'start_time', direction='backward')
                       
            # make df for grid condition that only contains ONE fixation per element
            # (the last fixation before the new element  (used a groupby.last() to achieve that))
            all_elements_df = make_df.make_all_elements_grid_df(merged_events)          
            
            # add a column for eyetracker and subject
            all_elements_df['et'] = et
            all_elements_df['subject'] = subject
            
            # concatenate to the complete df
            complete_small_large_grid_df = pd.concat([complete_small_large_grid_df,all_elements_df])
                   
    return complete_small_large_grid_df






#%% Create complete_freeview_df for all subjects



def get_complete_freeview_df(subjectnames, ets,**kwargs):
    # make the df for the large GRID for both eyetrackers and all subjects
    
    # create df
    complete_freeview_df = pd.DataFrame()
    complete_fix_count_df = pd.DataFrame()
        
    for subject in subjectnames:
        for et in ets:
            logging.critical('Eyetracker: %s    Subject: %s ', et, subject)
            
            # load preprocessed data for one eyetracker and for one subject
            #etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject, load=True)
            etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=True,**kwargs)
          
            
            # due to experimental triggers: FORWARD merge to add msgs to the events
            merged_events = helper.add_msg_to_event(etevents, etmsgs.query('condition=="FREEVIEW"'), timefield = 'start_time', direction='forward')
            
            # freeview df
            freeview_df, fix_count_df = make_df.make_freeview_df(merged_events)          
            
            # add a column for eyetracker and subject
            freeview_df['et'] = et
            fix_count_df['et'] = et
            freeview_df['subject'] = subject
            fix_count_df['subject'] = subject
            
            # concatenate to the complete dfs
            complete_freeview_df = pd.concat([complete_freeview_df,freeview_df])
            complete_fix_count_df = pd.concat([complete_fix_count_df,fix_count_df])
            
            
    return complete_freeview_df, complete_fix_count_df




 
#%% OLD
        
#%%     
        
#%% LOOK at GRID condition

experiment_start = etmsgs.query('condition=="startingET" & block == 1')

gridstart_time   = etmsgs.query(select + '& element == 1')
gridend_time     = etmsgs.query(select + '& element == 49')
grid_start_end   = pd.Series(sum(zip(gridstart_time.msg_time, gridend_time.msg_time), ()))

experiment_end   = etmsgs.query('condition=="Finished"')

# etevents['block']= pd.cut(etevents.start_time,pd.concat([gridstart_time.msg_time,experiment_end.msg_time]),labels = gridstart_time.block, include_lowest=True, right=True)

labels           = ["beginning"] + list([specifier + str(label) for label in gridstart_time.block for specifier in ('block_','other_')])
etevents['block']= pd.cut(etevents.start_time,pd.concat([experiment_start.msg_time, grid_start_end, experiment_end.msg_time],ignore_index = True),labels = labels, include_lowest=True, right=True)


# plot the mean fixation positions of all fixations during the grid condition
# get indices of event df that are within the time window and that are fixations
ix_grid_fix = (etevents.type == 'fixation')

        











#%% LOOK at GRID condition
# Only first block and only large Grid

# find out start and end  time of the large Grid condition
select = 'block == 1 & condition == "GRID" & grid_size == 49'
gridstart_time = etmsgs.query(select + '& element == 1').msg_time.values[0]
gridend_time = etmsgs.query(select + '& element == 49').msg_time.values[0]

# only focus on important columns and only consider samples that are labeled as fixations
ix_fix = (clean_etsamples.type == 'fixation') & ((clean_etsamples.smpl_time > gridstart_time) & (clean_etsamples.smpl_time < gridend_time))
reduced_clean_etsamples = clean_etsamples.loc[ix_fix,['gy', 'gx', 'smpl_time', 'type']]



#%% Plot with MATPLOTLIB
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


# plot the mean fixation positions of all fixations during the grid condition
axarr[1, 0].set_title('Gaze block 1 using events')

# get indices of event df that are within the time window and that are fixations
ix_grid_fix = ((etevents.start_time > gridstart_time) & (etevents.end_time < gridend_time)) & (etevents.type == 'fixation')
axarr[1, 0].plot(etevents.loc[ix_grid_fix, 'mean_gx'], etevents.loc[ix_grid_fix, 'mean_gy'],'o')


# plot the actual Grid and the recorded fixations in the same plot
axarr[1, 1].set_title('Overlaid plot')
axarr[1, 1].plot(x_grid_elements, y_grid_elements,'o')
axarr[1, 1].plot(etevents.loc[ix_grid_fix, 'mean_gx'], etevents.loc[ix_grid_fix, 'mean_gy'],'o')



#%% Trying to do the same with plotnine


# make a df that contains all grid element positions
grid_elements = pd.DataFrame(data=[etmsgs.query(select).groupby('element').first()['posx'].values, etmsgs.query(select).groupby('element').first()['posy'].values]).T
grid_elements.columns = ['posx_elem', 'posy_elem']


# Show stimulus Grid points
ggplot(grid_elements, aes(x='posx_elem', y='posy_elem')) + geom_point() + ggtitle("Grid points")

# Show all cleaned samples that are in selected condition and fixations
ggplot(reduced_clean_etsamples, aes(x='gx', y='gy')) + geom_point() + ggtitle('Gaze block 1 using all samples (only fixations)')

# Make a plot of the gridpoints and the data samples  (for block1)
ggplot(grid_elements, aes(x='posx_elem', y='posy_elem')) +\
        geom_point()+\
        geom_point(aes(x='gx', y='gy'), color='red',data = reduced_clean_etsamples)+\
        ggtitle('Gaze block 1 using all samples (only fixations)')



# select large Grid condition
select = 'condition == "GRID" & grid_size == 49'
gridstart_time = etmsgs.query(select + '& element == 1')
gridend_time = etmsgs.query(select + '& element == 49')

# only focus on important columns and only consider samples that are labeled as fixations
ix_fix = (clean_etsamples.type == 'fixation') 
reduced_clean_etsamples = clean_etsamples.loc[ix_fix,['gy', 'gx', 'smpl_time', 'type']]


# Make a plot of the gridpoints and the data samples  (for block1)
ggplot(grid_elements, aes(x='posx_elem', y='posy_elem')) +\
        geom_point()+\
        geom_point(aes(x='gx', y='gy'), color='red',data = reduced_clean_etsamples)+\
        facet_wrap('~block')+\
        ggtitle('Gaze block 1 using all samples (only fixations)')


# maybe try to do this without querying for blocks but using facets


# plot the mean fixation positions of all fixations during the grid condition
# get indices of event df that are within the time window and that are fixations
ix_grid_fix = (etevents.type == 'fixation')

ggplot(grid_elements, aes(x='posx_elem', y='posy_elem')) +\
        geom_point()+\
        geom_point(aes(x='mean_gx', y='mean_gy'), color='red',data = etevents.loc[ix_grid_fix])+\
        facet_wrap('~block')+\
        ggtitle('Gaze block 1 using events')


# maybe try to do this without querying for blocks but using facets
blockstarts   = etmsgs.query('condition=="startingET"')
experimentend = etmsgs.query('condition=="Finished"')
etevents['block']  = pd.cut(etevents.start_time,pd.concat([blockstarts.msg_time,experimentend.msg_time]),labels = blockstarts.block)

#TODO: all the exp_events end in _start and _stop
# Do i want the condition or the instruction??
instructions_starts  = etmsgs.query('exp_event=="BEGINNING_start"')
experiment_end        = etmsgs.query('exp_event=="BEGINNING_end"')
etevents['condition']  = pd.cut(etevents.start_time,pd.concat([instructions_starts.msg_time,experiment_end.msg_time]),labels = instructions_starts.condition)




#%% make a list of fixations between two stimuli

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



        














































# playing around with el blink dection

import functions.add_path
import numpy as np
import pandas as pd
import math
import time

import os,sys,inspect

import os
import matplotlib.pyplot as plt
from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
import functions.nbp_pupilhelper as nbp_pl
import functions.etcomp_parse as parse
import functions.detect_events as events
#import functions.pl_surface as pl_surface

# parses SR research EDF data files into pandas df
from pyedfread import edf

from functions import nbp_recalib

   
#%% HELPERS
    
def findFile(path,ftype):
    # finds file for el edf
    out = [edf for edf in os.listdir(path) if edf.endswith(ftype)]
    return(out)
  
#%% EYELINK

subject = 'inga_3'
datapath='/net/store/nbp/projects/etcomp/pilot'
# filepath for preprocessed folder
preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
# Load edf
filename = os.path.join(datapath,subject,'raw')

# elsamples:  contains individual EL samples
# elevents:   contains fixation and saccade definitions
# elnotes:    contains notes (meta data) associated with each trial
elsamples, elevents, elnotes = edf.pread(os.path.join(filename,findFile(filename,'.EDF')[0]), trial_marker=b'')


elevents.time.unique()

  
#%% Checking blink_id



# Probably not very interesting
elevents = events.el_make_events(subject)

plt.figure()
plt.plot(elevents.index, elevents.start, 'x', color='b')
plt.plot(elevents.index, elevents.end, 'x', color='b')

plt.plot(elevents.query("type=='blink'").index, elevents.query("type=='blink'").start, 'x', color='r')
plt.plot(elevents.query("type=='blink'").index, elevents.query("type=='blink'").end, 'x', color='r')

plt.plot(elevents.query("type=='fixation'").index, elevents.query("type=='fixation'").start, 'x', color='g')
plt.plot(elevents.query("type=='fixation'").index, elevents.query("type=='fixation'").end, 'x', color='g')

plt.plot(elevents.query("type=='saccade'").index, elevents.query("type=='saccade'").start, 'x', color='y')
plt.plot(elevents.query("type=='saccade'").index, elevents.query("type=='saccade'").end, 'x', color='y')


  
#%% 

   # remove to large pa    
    # TODO : we dropped this cause pa mostly look good after removing pa == 0 
    # check pa / diameter large values inga_3 end
    # Pupil Area is unreasonably large
    # As there will be very different absolute pa sizes, we will do outlier detection ? 
#    # keep only the ones that are within +3 to -3 standard deviations
#    marked_samples['too_large_pa'] = np.abs(etsamples.pa-np.nanmean(etsamples.pa))>(3* (np.nanstd(etsamples.pa)))
#    
#    # add columns to the samples df
#    marked_samples = pd.concat([etsamples, marked_samples], axis=1)
#
#    plt.figure()
#    plt.plot(etsamples['smpl_time'], etsamples['pa'], 'x', color='b')
#    plt.plot(marked_samples.query('too_large_pa==1')['smpl_time'], marked_samples.query('too_large_pa==1')['pa'], 'o', color='r')
#    etsamples['pa'].describe()
    



  
#%% 

# have a look at the data

# samples df
plsamples.info()
plsamples.describe()
elsamples.info()
elsamples.describe()


# msgs df
plmsgs.info()
plmsgs.describe()
elmsgs.info()
elmsgs.describe()

# TODO: Why do we find a missmatch here?
elmsgs.condition.value_counts()
plmsgs.condition.value_counts()


# epochs df
elepochs.info()
elepochs.describe()
plepochs.info()
plepochs.describe()


# look how many samples that can be used for each condition
plepochs.condition.value_counts()
elepochs.condition.value_counts()



   
#%% SANITY CHECKS

# msgs EL
elmsgs.info()
set(elmsgs['pic_id'].unique()) - set(plmsgs['pic_id'].unique()) 
















#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 11:51:36 2018

@author:  kgross
"""
import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import functions.et_plotting as etplot
import functions.et_preprocess as preprocess
import functions.et_make_df as df
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.pl_detect_blinks as pl_blinks


from functions.detect_events import make_blinks,make_saccades,make_fixations





import functions.detect_bad_samples as detect_bad_samples

#%% LOOK at GRID condition
# Only first block and only large Grid

# epoch etdata according to query
condquery = '((condition == "GRID" & grid_size == 49.0 & block == 1)'

# remove bad samples
clean_elsamples = detect_bad_samples.remove_bad_samples(elsamples)

# make epochs
elepochs = df.make_epochs(clean_elsamples, elmsgs.query(condquery))
# only focus on important columns and only consider samples that are labeled as fixations
reduced_elepochs = elepochs.loc[:,['gy', 'gx', 'smpl_time', 'type', 'td', 'block', 'condition', 'exp_event', 'msg_time', 'element', 'grid_size', 'posx', 'posy']]
reduced_elepochs = reduced_elepochs.query('type == "fixation"', inplace=True)



#%% Plot
figure, axarr = plt.subplots(2, 2)

# Show stimulus Grid points
axarr[0, 0].set_title('Grid that was shown in block 1')
# get all gridpoints that were shown on the screen
x_grid_elements = reduced_elepochs.groupby('element').first()['posx']
y_grid_elements = reduced_elepochs.groupby('element').first()['posy']
axarr[0, 0].plot(x_grid_elements, y_grid_elements,'o')


# use all samples that are within 2 sec of a msg and that are labeled as fixations
axarr[0, 1].set_title('Gaze block 1 using all samples (only fixations)')
axarr[0, 1].plot(reduced_elepochs.gx, reduced_elepochs.gy,'o')


# plot the mean fixation positions of all fixations during the grid condition
axarr[1, 0].set_title('Gaze block 1 using events')

# find out start and end  time of the large Grid condition
select = 'block == 1 & condition == "GRID" & grid_size == 49'
gridstart_time = elmsgs.query(select + '& element == 1').msg_time.values[0]
gridend_time = elmsgs.query(select + '& element == 49').msg_time.values[0]
# get indices of event df that are within the time window and that are fixations
ix_grid_fix = ((elevents.start_time > gridstart_time) & (elevents.end_time < gridend_time)) & (elevents.type == 'fixation')

axarr[1, 0].plot(elevents.loc[ix_grid_fix, 'mean_gx'], elevents.loc[ix_grid_fix, 'mean_gy'],'o')


# plot the actual Grid and the recorded fixations in the same plot
axarr[1, 1].set_title('Overlaid plot')
axarr[1, 1].plot(elevents.loc[ix_grid_fix, 'mean_gx'], elevents.loc[ix_grid_fix, 'mean_gy'],'o')
axarr[0, 1].plot(reduced_elepochs.gx, reduced_elepochs.gy,'o')






#%%

#%%


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


#%% PUPIL DILATION

# Looking at dilation data

elepochs.lum.unique()

# EL
etplot.plot_diam(elepochs,query='condition=="DILATION" & block==1 & lum==255')

# PL
etplot.plot_diam(plepochs, query='condition=="DILATION" & block==1 & lum==64')

etplot.plotTraces(plepochs, y='pa', query='condition=="DILATION" & lum==64')
etplot.plotTraces(elepochs, y='pa', query='condition=="DILATION" & block==1 & lum==255')


#%%

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


#%%

# Plot Blinks PL

plt.plot(plsamples.smpl_time, plsamples.confidence, 'o')
plt.plot(plsamples.query('type=="blink"')['smpl_time'], plsamples.query('type=="blink"')['confidence']+0.01, 'o')
plt.plot(plsamples['smpl_time'], plsamples['blink_id'], 'o')



#%%

    
#    if len(np.intersect1d(etmsgs.columns,etevents.columns)) is not 0:
#        raise Exception('Some fields of etmsgs are already defined in etevents')
#            
#    for col in etmsgs.columns:
#        etevents[col] = pd.cut(etevents[timefield],[etmsgs.msg_time],labels=etmsgs.loc[1:-1,col])
#  

#%%

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



