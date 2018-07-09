#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 12:21:32 2018

@author: kgross
"""


import functions.add_path
import numpy as np
import time

import os
import av

from lib.pupil.pupil_src.shared_modules import offline_surface_tracker

from offline_reference_surface import Offline_Reference_Surface

import logging
logging.basicConfig(level=logging.DEBUG)

from functions.pl_recalib import gen_fakepool
from functions.pl_recalib import global_container
from queue import Empty as QueueEmptyException


from camera_models import load_intrinsics

from player_methods import correlate_data

datapath='/net/store/nbp/projects/etcomp/'
subject = 'VP1'
folder= os.path.join(datapath,subject,'raw')

def fake_gpool_surface(folder = None):
    if not folder:
        raise('we need the folder else we cannot load timestamps and surfaces etc.')
    surface_dir = os.path.join(folder,'../','surface')
    if not os.path.exists(surface_dir):
        os.makedirs(surface_dir)


    fake_gpool = gen_fakepool()
    fake_gpool.surfaces = []
    fake_gpool.rec_dir = surface_dir
    fake_gpool.timestamps = np.load(os.path.join(folder,'world_timestamps.npy'))
    fake_gpool.capture.source_path = os.path.join(folder,'world.mp4')
    fake_gpool.capture.intrinsics = load_intrinsics('','Pupil Cam1 ID2',(1280, 720))
    fake_gpool.seek_control = global_container()
    fake_gpool.seek_control.trim_left = 0
    fake_gpool.seek_control.trim_right = 0
    fake_gpool.timeline = global_container()
    return(fake_gpool)
    
def surface_map_data(tracker,data):
    if not (type(data) == list):
        raise 'Did you forget to select what data? I expected a list here'
    
    # get the gaze positions in world-camera units
    fake_gpool = tracker.g_pool
    fake_gpool.gaze_positions = data
    fake_gpool.gaze_positions_by_frame = correlate_data(fake_gpool.gaze_positions, fake_gpool.timestamps)
    
    if not(len(tracker.surfaces) == 1):
        raise 'expected only a single surface!'
    # And finally calculate the positions 
    gaze_on_srf  = tracker.surfaces[0].gaze_on_srf_in_section()
    
    
              
fake_gpool = fake_gpool_surface(folder)

tracker = offline_surface_tracker.Offline_Surface_Tracker(fake_gpool,min_marker_perimeter=30,robust_detection=False)
#%%

def map_surface(folder,loadCache = True,loadSurface = True):
    # if you want to redo it, put loadCache to false
    
    # How a surface in pupil labs works (took me many days to figure that out...)
    #  1. detect all markers in tracker (this starts its own slave process)
    #  2. add some markers to a surface via build_correspondence
    #  3. for all markers detect the surface (init_cache)
    #  4. add the surface to the tracker
    #  5. map the observed pupil data to the surface (done in surface_map_data)
    
                
    fake_gpool = fake_gpool_surface(folder)

    
    # Step 1.    
    print('Starting Tracker - WARNING: ROBUST_DETECTION IS CURRENTLY FALSE')
    # TODO Decide robust detection (not really sure what it does)
    tracker = offline_surface_tracker.Offline_Surface_Tracker(fake_gpool,min_marker_perimeter=30,robust_detection=False)
    tracker.timeline = None
    
    if loadSurface and len(tracker.surfaces)==1 and tracker.surfaces[0].defined:
        print('Surface already defined, loadSurface=TRUE, thus returning tracker')
        tracker.cleanup()
        return(tracker)
    # Remove the cache if we do not need it
    if not loadCache:
        tracker.invalidate_marker_cache()
    
    start = time.time()
    
    print('Finding Markers')
    # This does what offline_surface_tracker.update_marker_cache() does (except the update surface, we dont need it), 
    # but in addition gives us feedback & has a stopping criterion
    while True:
        if (time.time()-start)>1:
            start = time.time()        
            visited_list = [False if x is False else True for x in tracker.cache]
            percent_visited = np.mean(np.asarray(visited_list))
            print(percent_visited)
            if percent_visited == 1:
                # save stuff and stop the process   
                tracker.cleanup()
                break
        try:
            idx, c_m = tracker.cache_queue.get(timeout=5)
        except QueueEmptyException:
            time.sleep(1)
            
            print('Nothing to do, waiting...')
            continue
        tracker.cache.update(idx, c_m)
        
     
        if tracker.cacher_run.value is False:
            tracker.recalculate()
        
    
    
    # Step 2.    
    # add a single surface
    print('Adding a surface')
    surface = Offline_Reference_Surface(tracker.g_pool)    
    
    
    # First define the markers that should be used for the surface
    # find a frame where there are 16 markers and all of them have high confidence
    ix = 0
    while True:
        if len(tracker.cache[ix]) == 16:
            usable_markers = [m for m in tracker.cache[ix] if m['id_confidence'] >= 0.8]
            if len(usable_markers) == 16:
                break
        ix +=ix
        
    # Step 3
    # This dissables pupil-labs functionality. They ask for 90 frames with the markers. but because we know there will be 16 markers, we dont need it (toitoitoi)
    print('Defining & Finding Surface')
    surface.required_build_up = 1
    surface.build_correspondence(tracker.cache[ix],0.3,0.7)
    if not surface.defined:
        raise('Oh oh trouble ahead. The surface was not defined')
    surface.init_cache(tracker.cache,0.3,0.7)
    
    # Step 4
    tracker.surfaces = [surface];


    
    print('Saving Surface')
    tracker.save_surface_definitions_to_file()
    return(surface)

    return(gaze_on_srf)