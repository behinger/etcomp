import functions.add_path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




def nbp_pupildetect(eye_id = None,folder=None,pupildetect_options = None,detector_type='2D'):
    import av
    import ctypes
    ctypes.cdll.LoadLibrary('/net/store/nbp/users/behinger/projects/etcomp/local/build/build_ceres_working/lib/libceres.so.2')
    import pupil_producers as pupil_produce
    import pupil_detectors
    from functions.pl_surface import fake_gpool_surface
    import pl_anna_tools
    from ui_roi import UIRoi

    
    #options = {"pupil_size_min":10,'pupil_size_max':150}
    
    
    
    cap = pl_anna_tools.init_playback(video_name = 'eye'+str(eye_id)+'.mp4',video_file_path = folder)

    
    #result = detector.detect(frame, UIRoi([frame.height,frame.width]), 0)
    if detector_type == '2D':
        detector = pupil_detectors.Detector_2D()
    elif detector_type == '3D':
        detector = pupil_detectors.Detector_3D()
    else:
        raise('unknowpln detectortype')
        
    if pupildetect_options:
        # XXX to be implemented after looking at what these parameters do.........
        for key in options.keys():
            assert key in detector.detectProperties.keys()



    results = [];
    for k in range(cap.get_frame_count()):
        cap.seek_to_frame(k)
        frame = cap.get_frame()
        result = detector.detect(frame, UIRoi([frame.height,frame.width]), 0)
        if result is not None:
            result['id'] = eye_id
        results.append(result)
    return(results)