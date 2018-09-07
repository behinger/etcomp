# -*- coding: utf-8 -*-

import functions.add_path

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *

import functions.et_make_df as make_df
import functions.et_helper as  helper
import functions.et_plotting as etplot
import functions.detect_events as events
import functions.detect_saccades as saccades
import functions.et_preprocess as preprocess
import functions.pl_detect_blinks as pl_blinks
from functions.et_make_df import make_epochs
from functions.detect_events import make_blinks,make_saccades,make_fixations


#%% imports for plotting the analysis

import LARGE_GRID 
import LARGE_and_SMALL_GRID
import FREEVIEW
import functions.et_condition_df as condition_df


from matplotlib import interactive
interactive(True)


#%% specify ALL subjects names

# to initialize logging
import functions.init_logger
import logging


# loop over the foldernames (subjectnames)
# restricted to subjects that we do not exclude from analysis
# also loop over the et
foldernames       = helper.get_subjectnames('/net/store/nbp/projects/etcomp/')

# TODO find out whats wrong with vp3 and vp12 and fix and then use vp3 again!!
rejected_subjects = ['pilot', 'log_files', 'surface', 'results', '007', 'VP8', 'VP21','VP7']
subjectnames      = [subject for subject in foldernames if subject not in rejected_subjects]
ets               = ['el', 'pl']    


# get a logger
logger = logging.getLogger(__name__)



#%% preprocess for all subjects
for subject in subjectnames:
    for et in ets:
        logger.critical(' ')
        logger.critical('Eyetracker: %s    Subject: %s ', et, subject)
        etsamples, etmsgs, etevents = preprocess.preprocess_et(et,subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))


#%% CALCULATE data and preprocess RAW data for ONE subject

# specify subject
subject = 'VP4'

# preprocess pl data
plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))

# preprocess el data
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=False,save=True,eventfunctions=(make_blinks,make_saccades,make_fixations))



#%% LOAD preprocessed data for ONE subject from csv file

# specify subject
subject = 'VP4'


plsamples, plmsgs, plevents = preprocess.preprocess_et('pl',subject,load=True)
elsamples, elmsgs, elevents = preprocess.preprocess_et('el',subject,load=True)



# which et do you want to examine?
et_str = 'pl'
etsamples = plsamples
etmsgs = plmsgs
etevents = plevents
# or
et_str = 'el'
etsamples = elsamples
etmsgs = elmsgs
etevents = elevents


# have a look at time and gx
plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')



#%% Figure to examine which samples we exclude

# get uncleaned data samples
datapath='/net/store/nbp/projects/etcomp/'
preprocessed_path = os.path.join(datapath, subject, 'preprocessed')
etsamples = pd.read_csv(os.path.join(preprocessed_path,str(et_str+'_samples.csv')))

# look at horizontal gaze component
plt.figure()
plt.plot(etsamples['smpl_time'],etsamples['gx'],'o')

plt.plot(etsamples.query('type=="blink"')['smpl_time'],etsamples.query('type=="blink"')['gx'],'o')
plt.plot(etsamples.query('type=="saccade"')['smpl_time'],etsamples.query('type=="saccade"')['gx'],'o')
plt.plot(etsamples.query('type=="fixation"')['smpl_time'],etsamples.query('type=="fixation"')['gx'],'o')
plt.legend(['sample','blink','saccade','fixation'])

# title specifies eye tracker and subject
plt.title(str(et_str + " " + subject))

# if you want to look at the not cleaned data, you should set the yaxis
plt.ylim([-50,2500])


plt.plot(etsamples.query('neg_time==True')['smpl_time'],etsamples.query('neg_time==True')['gx'],'o')
plt.plot(etsamples.query('outside==True')['smpl_time'],etsamples.query('outside==True')['gx'],'o')
plt.plot(etsamples.query('zero_pa==True')['smpl_time'],etsamples.query('zero_pa==True')['gx'],'o')



#%% Call plots from analysis here


# change into code folder
# TODO this should not be necessary
os.chdir('/net/store/nbp/users/kgross/etcomp/code')

# only for test, so you dont have to load so many
# subjectnames      = ['VP3', 'VP4', 'VP1', 'VP14', 'VP2', 'VP11', 'VP26', 'VP25']


############
# LARGE GRID

# load grid df for subjectnames
raw_large_grid_df = condition_df.get_condition_df(subjectnames, ets, condition='LARGE_GRID')

# plot accuracy    
LARGE_GRID.plot_accuracy(raw_large_grid_df)

LARGE_GRID.plot_accuracy(raw_large_grid_df, option='variance_within_block')

# plot accuracy components
LARGE_GRID.compare_accuracy_components(raw_large_grid_df)
LARGE_GRID.compare_accuracy_components(raw_large_grid_df, display_precision=True)

# look at numerical accuracies in table
table_large_grid_accuracy = LARGE_GRID.make_table_accuracy(raw_large_grid_df)
table_large_grid_accuracy = LARGE_GRID.make_table_accuracy(raw_large_grid_df, concise=True)
print(table_large_grid_accuracy.to_string())


# investigate on the position and properties of detected fixations
LARGE_GRID.display_fixations(raw_large_grid_df, option='fixations')
LARGE_GRID.display_fixations(raw_large_grid_df, option='fixations', greyscale=True)
LARGE_GRID.display_fixations(raw_large_grid_df, option='offset')
LARGE_GRID.display_fixations(raw_large_grid_df, option='offset', greyscale=True)


# TODO check the ones below
LARGE_GRID.display_fixations(raw_large_grid_df, option='accuracy_for_each_element')
LARGE_GRID.display_fixations(raw_large_grid_df, option='precision_for_each_element')




######################
# LARGE and SMALL GRID
raw_all_grids_df = condition_df.get_condition_df(subjectnames, ets, condition='LARGE_and_SMALL_GRID')


# plot accuracy  
p = LARGE_and_SMALL_GRID.plot_accuracy(raw_all_grids_df, option='final_figure')
p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' +'course_of_accuracy.png'), height=8, width=7, units = 'in', dpi=500)

LARGE_and_SMALL_GRID.plot_accuracy(raw_all_grids_df, option=None)
LARGE_and_SMALL_GRID.plot_accuracy(raw_all_grids_df, option='facet_subjects')
LARGE_and_SMALL_GRID.plot_accuracy(raw_all_grids_df, option='show_variance_for_blocks')

# investigate on the position and properties of detected fixations
LARGE_and_SMALL_GRID.display_fixations(raw_all_grids_df, option='fixations')




#############
# Freeviewing
raw_freeview_df, raw_fix_count_df = condition_df.get_condition_df(subjectnames, ets, condition='FREEVIEW')

# plot the fixations as a heatmap
# TODO annotation how many fixations from how many pictures are used for each eyetracker
FREEVIEW.plot_heatmap(raw_freeview_df)

# plot fixation counts
FREEVIEW.plot_number_of_fixations(raw_fix_count_df, option=None)
FREEVIEW.plot_number_of_fixations(raw_fix_count_df, option='violin')

# just to have a look at the different fix_counts for each picture in each subject
FREEVIEW.plot_number_of_fixations(raw_fix_count_df, option='facet_subjects')

# TODO
# plot histogram of the counts
FREEVIEW.plot_histogram(raw_fix_count_df)

# plot fixation durations
FREEVIEW.plot_fixation_durations(raw_freeview_df)
FREEVIEW.plot_fixation_durations(raw_freeview_df, option='facet_subjects')




################
# main sequence
# TODO plot main sequence
FREEVIEW.plot_main_sequence(raw_freeview_df)




subject = 'VP4'
block = None
condition = None


# TODO compare raw signal



def compare_raw_signal(subject, block, condition, algorithm=None):
    """
    TODO
    shows raw signal for each eyetracker.
    Colors indicate detected events
    """
    

    datapath = '/net/store/nbp/projects/etcomp/'
    all_samples = pd.DataFrame()
    etmsgs= pd.DataFrame()
    etevents = pd.DataFrame()

    etgrid   = pd.DataFrame()


    for et in ['el','pl']:

        etsamples, elmsgs, etevents = preprocess.preprocess_et(et, subject,load=True)

        # time window depends on condition and block
        # TODO
        t0 = elmsgs.query("condition=='Instruction'&exp_event=='BEGINNING_start'").msg_time.values
        if len(t0)!=1:
            raise error
        etsamples.smpl_time = etsamples.smpl_time - t0

        tstart = 220
        tdur =50
        
        
        all_samples = pd.concat([all_samples,etsamples.assign(eyetracker=et)],ignore_index=True, sort=False)
        etmsgs    = pd.concat([etmsgs,      elmsgs.assign(eyetracker=et)],ignore_index=True, sort=False)
        etevents  = pd.concat([etevents,  etevents.assign(eyetracker=et)],ignore_index=True, sort=False)
        
        etgrid  = pd.concat([etgrid,  etgrid.assign(eyetracker=et)],ignore_index=True, sort=False)
            

    return (ggplot(all_samples.query("smpl_time>%i & smpl_time<%i"%(tstart,tstart+tdur)),aes(x="smpl_time",y="gx",color="type"))+
                 geom_point()+
                 facet_grid("eyetracker~."))

      


compare_raw_signal("VP1", 1, 1)







######## SAVING the plots##########

p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' + str(eyetracker)[2:-2] +' displayed_fixations.svg'), height=15, width=15, units = 'in', dpi=1000)
p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' + str(eyetracker)[2:-2] +' meanelem_medianblock.png'), height=15, width=10, units = 'in', dpi=500)

# bene prefers pdfs
p.save(filename = str('../plots/2018-09-05_tea_time_presentation/' + str(eyetracker)[2:-2] +' displayed_fixations.pdf'), height=15, width=15, units = 'in', dpi=1000)


# subplot adjust
p.subplot_adjust = 0.85
p
