#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 11:41:34 2018

@author: behinger
"""


import functions.add_path
import numpy as np
import pandas as pd
import time

import os
import matplotlib.pyplot as plt
import functions.nbp_pupilhelper as nbp_pl
import av

from lib.pupil.pupil_src.shared_modules import offline_surface_tracker


from functions import nbp_recalib

from offline_reference_surface import Offline_Reference_Surface



from functions.pl_recalib import gen_fakepool
from functions.pl_recalib import global_container
from queue import Empty as QueueEmptyException


from camera_models import load_intrinsics


from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
from player_methods import correlate_data

#%%


#%%
datapath = '/net/store/nbp/projects/etcomp/pilot'
subject = 'katha'


filename = os.path.join(datapath,subject,'raw')

# TODO: Change the recording folder to /net/store.../etcomp/inga/surface - else we are in trouble!
fake_gpool = gen_fakepool()
fake_gpool.surfaces = []
fake_gpool.timestamps = np.load(os.path.join(filename,'world_timestamps.npy'))
fake_gpool.capture.source_path = os.path.join(filename,'world.mp4')
fake_gpool.capture.intrinsics = load_intrinsics('','Pupil Cam1 ID2',(1280, 720))
fake_gpool.seek_control = global_container()
fake_gpool.seek_control.trim_left = 0
fake_gpool.seek_control.trim_right = 0
fake_gpool.timeline = global_container()
#%%
# I think in principle we could also run
#   def fill_cache(visited_list, video_file_path, q, seek_idx, run, min_marker_perimeter, invert_image): from marker_detector_cacher directly

tracker = offline_surface_tracker.Offline_Surface_Tracker(fake_gpool,min_marker_perimeter=30,robust_detection=False)
tracker.timeline = None

start = time.time()
while True:
    #while not tracker.cache_queue.empty():
    try:
        idx, c_m = tracker.cache_queue.get(timeout=5)
    except QueueEmptyException:
        time.sleep(1)
        print('Nothing to do, waiting...')
        continue
    tracker.cache.update(idx, c_m)
    #print(tracker.cache_queue.qsize())
    if (time.time()-start)>1:
        start = time.time()        
        visited_list = [False if x is False else True for x in tracker.cache]
        print(np.mean(np.asarray(visited_list)))


tracker.cleanup()

# new surface
surface = Offline_Reference_Surface(tracker.g_pool)    
tracker.surfaces.append(surface)



# First (somehow) define the markers that should be used for the surface


# not sure if this is the way

surface.build_correspondence(tracker.cache,0.3,0.7)


# then fit the surface
surface.init_cache(tracker.cache,0,0)


# load the data and add it to the linked fake_gpool
pldata = pl_file_methods.load_object(os.path.join(filename,'pupil_data'))

# get the gaze poisitions in world-camera units
# This is exactly the problem, because then we have only a 60 Hz signal...anyway
fake_gpool.gaze_positions = pldata['gaze_positions']
fake_gpool.gaze_positions_by_frame = correlate_data(fake_gpool.gaze_positions, fake_gpool.timestamps)

# And finally calculate the positions 
gaze_on_srf  = surface.gaze_on_srf_in_section()




## redo the whole surface mapping


# find surfaces
#this reliably crashes my python
#tracker.surfaces.append(Offline_Reference_Surface(tracker.g_pool))

 
