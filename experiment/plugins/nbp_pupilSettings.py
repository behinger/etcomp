import msgpack
import os


if 1 ==0:

    def load_object(file_path,allow_legacy=True):
        import gc
        file_path = os.path.expanduser(file_path)
        with open(file_path, 'rb') as fh:
            try:
                gc.disable()  # speeds deserialization up.
                data = msgpack.unpack(fh, encoding='utf-8')
            except Exception as e:
                if not allow_legacy:
                    raise e
                else:
                    logger.info('{} has a deprecated format: Will be updated on save'.format(file_path))
                    data = _load_object_legacy(file_path)
            finally:
                gc.enable()
        return data
    load_object('~/pupil_capture_settings/user_settings_world')

def save_object(object_, file_path):
    # taken from pupillabs
    def ndarrray_to_list(o, _warned=[False]): # Use a mutlable default arg to hold a fn interal temp var.
        if isinstance(o, np.ndarray):
            if not _warned[0]:
                logger.warning("numpy array will be serialized as list. Invoked at:\n"+''.join(tb.format_stack()))
                _warned[0] = True
            return o.tolist()
        return o

    file_path = os.path.expanduser(file_path)
    with open(file_path, 'wb') as fh:
        msgpack.pack(object_, fh, use_bin_type=True,default=ndarrray_to_list)

eye = {'capture_manager_settings': ['UVC_Manager', {}],
       'capture_settings': ['UVC_Source',
          {'frame_rate': 120,
           'frame_size': [640, 480],
           'name': 'Pupil Cam1 ID0',
           'uvc_controls': {'Absolute Exposure Time': 63,
            'Auto Exposure Mode': 1,
            'Auto Exposure Priority': 0,
            'Backlight Compensation': 2,
            'Brightness': 0,
            'Contrast': 32,
            'Gain': 0,
            'Gamma': 100,
            'Hue': 0,
            'Power Line frequency': 1,
            'Saturation': 0,
            'Sharpness': 2,
            'White Balance temperature': 4600,
            'White Balance temperature,Auto': 1}}],
     'display_mode': 'camera_image',
     'flip': True,
     'gui_scale': 1.0,
     'last_pupil_detector': 'Detector_3D',
     'pupil_detector_settings': {'2D_Settings': {'blur_size': 5,
       'canny_aperture': 5,
       'canny_ration': 2,
       'canny_treshold': 160,
       'coarse_detection': True,
       'coarse_filter_max': 280,
       'coarse_filter_min': 128,
       'contour_size_min': 5,
       'ellipse_roundness_ratio': 0.1,
       'ellipse_true_support_min_dist': 2.5,
       'final_perimeter_ratio_range_max': 1.2,
       'final_perimeter_ratio_range_min': 0.6,
       'initial_ellipse_fit_treshhold': 1.8,
       'intensity_range': 23,
       'pupil_size_max': 300.0,
       'pupil_size_min': 20.0,
       'strong_area_ratio_range_max': 1.1,
       'strong_area_ratio_range_min': 0.6,
       'strong_perimeter_ratio_range_max': 1.1,
       'strong_perimeter_ratio_range_min': 0.8},
      '3D_Settings': {'model_sensitivity': 0.997}},
     'roi': [1, 1, 639, 479, [480, 640]],
     'ui_config': {'submenus': {'Icons': [{'collapsed': False,
         'min_size': [0.0, 0.0],
         'pos': [-50.0, 0.0],
         'scrollstate': [0.0, 0.0],
         'size': [0.0, 0.0],
         'submenus': {}}],
       'Settings': [{'collapsed': False,
         'min_size': [300.0, 20.0],
         'pos': [-500.0, 0.0],
         'scrollstate': [0.0, 0.0],
         'size': [-50.0, 0.0],
         'submenus': {'Backend Manager': [{'collapsed': True,
            'pos': [0.0, 0.0],
            'size': [0.0, 0],
            'submenus': {}}],
          'General': [{'collapsed': True,
            'pos': [0.0, 0.0],
            'size': [0.0, 0],
            'submenus': {}}],
          'Local USB Source: Pupil Cam1 ID0': [{'collapsed': False,
            'pos': [0.0, 0.0],
            'size': [0.0, 0],
            'submenus': {'Image Post Processing': [{'collapsed': True,
               'pos': [0.0, 0.0],
               'size': [0.0, 0],
               'submenus': {}}],
             'Sensor Settings': [{'collapsed': False,
               'pos': [0.0, 0.0],
               'size': [0.0, 0],
               'submenus': {}}]}}],
          'Pupil Detector 3D': [{'collapsed': True,
            'pos': [0.0, 0.0],
            'size': [0.0, 0],
            'submenus': {}}]}}]}},
     'version': '1.6.13',
     'window_position': [1231, 542],
     'window_size': [690, 480]}



world = {'audio_mode': 'voice and sound',
 'detection_mapping_mode': '3d',
 'eye0_process_alive': True,
 'eye1_process_alive': False,
 'gui_scale': 1.0,
 'loaded_plugins': [['UVC_Source',
   {'frame_rate': 60,
    'frame_size': [1280, 720],
    'preferred_names': ['Pupil Cam1 ID2',
     'Logitech Camera',
     '(046d:081d)',
     'C510',
     'B525',
     'C525',
     'C615',
     'C920',
     'C930e']}],
  ['Pupil_Data_Relay', {}],
  ['Pupil_Remote',
   {'host': '100.1.0.3', 'port': '5004', 'use_primary_interface': 0}],
  ['Dummy_Gaze_Mapper', {}],
  ['Log_Display', {}],
  ['UVC_Manager', {}],
  ['Screen_Marker_Calibration',
   {'fullscreen': True, 'marker_scale': 1.0, 'monitor_name': b'DVI-I-1'}],
  ['Plugin_Manager', {}],
  ['System_Graphs',
   {'show_conf0': True,
    'show_conf1': True,
    'show_cpu': True,
    'show_dia0': False,
    'show_dia1': False,
    'show_fps': True}],
  ['Display_Recent_Gaze', {}],
  ['Accuracy_Visualizer',
   {'outlier_threshold': 5.0, 'vis_mapping_error': True}],
  ['Recorder',
   {'info_menu_conf': {},
    'raw_jpeg': True,
    'rec_dir': '/home/experiment/recordings',
    'record_eye': True,
    'session_name': '2018_04_09',
    'show_info_menu': False,
    'user_info': {'additional_field': 'change_me', 'name': ''}}]],
 'min_calibration_confidence': 0.8,
 'ui_config': {'submenus': {'Icons': [{'collapsed': False,
     'min_size': [0.0, 0.0],
     'pos': [-50.0, 0.0],
     'scrollstate': [0.0, 0.0],
     'size': [0.0, 0.0],
     'submenus': {}}],
   'Quick Bar': [{'collapsed': False,
     'pos': [0.0, 100.0],
     'size': [120.0, -100.0],
     'submenus': {}}],
   'Settings': [{'collapsed': False,
     'min_size': [300.0, 20.0],
     'pos': [-400.0, 0.0],
     'scrollstate': [0.0, 0.0],
     'size': [-50.0, 0.0],
     'submenus': {'Accuracy Visualizer': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'Backend Manager': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'Dummy gaze mapper': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'General': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'Local USB Source: Ghost capture': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'Plugin Manager': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'Pupil Remote': [{'collapsed': False,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'Recorder': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'Screen Marker Calibration': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}],
      'System Graphs': [{'collapsed': True,
        'pos': [0.0, 0.0],
        'size': [0.0, 0],
        'submenus': {}}]}}]}},
 'version': '1.6.13',
 'window_position': [30, 52],
 'window_size': [1330, 720]}



user_dir = os.path.expanduser(os.path.join('~', 'pupil_capture_settings'))

save_object(eye,os.path.join(user_dir,'user_settings_eye0'))

save_object(eye,os.path.join(user_dir,'user_settings_eye1'))

save_object(world,os.path.join(user_dir,'user_settings_world'))
print('Successfully loaded nbp-pupil settings - world:60hz@1280x1024, binocular:120Hz@640x480')
