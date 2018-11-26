import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


import functions.et_preprocess as preprocess


import functions.pl_surface as pl_surface
from functions import et_import
from lib.pupil.pupil_src.shared_modules import accuracy_visualizer
from functions.pl_recalib import pl_recalibV2

import logging
import av,os

import ctypes
ctypes.cdll.LoadLibrary('/net/store/nbp/users/behinger/projects/etcomp/local/build/build_ceres_working/lib/libceres.so.2')


# Pretty serious workaround. Ignores errors in imports :S
import builtins
from types import ModuleType
import pupil_detectors
class DummyModule(ModuleType):
    def __getattr__(self, key):
        return None
    __all__ = []   # support wildcard imports

def tryimport(name, *args, **kwargs):
    try:
        imp = realimport(name, *args,**kwargs)
        #print('success: '+name)
        return imp 
    except Exception as e:
        print('reached exception:' + name)
        if name =='cPickle': # because how they import cPickle/Pickle
            return realimport('pickle', *args,**kwargs)    
        
        #print(e)
        return DummyModule(name)



realimport, builtins.__import__ = builtins.__import__, tryimport
try:
    from video_capture import init_playback_source


except Exception as e:
    print('-------------------')
    print(e)
    pass
tryimport, builtins.__import__ = builtins.__import__, realimport



def init_playback(video_name = 'world.mp4',video_file_path = None):

    class Global_Container(object):
        pass



    cap = init_playback_source(Global_Container(), os.path.join(video_file_path,video_name))
    return(cap)



def nbp_pupildetect(eye_id = None,folder=None,pupildetect_options = None,detector_type='2d'):
    

    
    from functions.pl_surface import fake_gpool_surface
    from ui_roi import UIRoi
    
    #options = {"pupil_size_min":10,'pupil_size_max':150}
    
    
    logger = logging.getLogger(__name__)
    logger.info("Redetecting Pupil")
    logger.info("Starting Playback Device")
    
    cap = init_playback(video_name = 'eye'+str(eye_id)+'.mp4',video_file_path = folder)

    logger.info("Detector_type:"+detector_type)
    #result = detector.detect(frame, UIRoi([frame.height,frame.width]), 0)
    if detector_type == '2d':
        detector = pupil_detectors.Detector_2D()
    elif detector_type == '3d':
        detector = pupil_detectors.Detector_3D()
    else:
        print("unknown detector type:"+detector_type)
        raise('unknown detectortype')
        
    if pupildetect_options:
        # XXX to be implemented after looking at what these parameters do.........
        for key in options.keys():
            assert key in detector.detectProperties.keys()


    logger.info("Starting detection of eye"+str(eye_id))
    results = [];
    for k in range(cap.get_frame_count()):
        cap.seek_to_frame(k)
        frame = cap.get_frame()
        result = detector.detect(frame, UIRoi([frame.height,frame.width]), 0)
        if result is not None:
            result['id'] = eye_id
        results.append(result)
    return(results)