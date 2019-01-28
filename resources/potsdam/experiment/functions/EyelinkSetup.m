function EyelinkSetup

% remote mode possible add HTARGET ( head target)
% Eyelink('command', 'file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT');
% Eyelink('command', 'file_sample_data  = LEFT,RIGHT,GAZE,HREF,AREA,GAZERES,STATUS,INPUT,HTARGET');

% set link data (used for gaze cursor)
% Eyelink('command', 'link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,FIXUPDATE,INPUT');
% Eyelink('command', 'link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT,HTARGET');

% set EDF file contents
Eyelink('command', 'file_event_filter = LEFT,RIGHT,MESSAGE');
Eyelink('command', 'file_sample_data  = LEFT,RIGHT,GAZE,AREA');

% set link data (used for gaze cursor)
Eyelink('command', 'link_event_filter = LEFT,RIGHT,BUTTON');
Eyelink('command', 'link_sample_data  = LEFT,RIGHT,GAZE,AREA');

% set up tracker configuration
Eyelink('command', 'calibration_type = HV9');   

% set pupil Tracking model in camera setup screen
% no = centroid. yes = ellipse
% Eyelink('command', 'use_ellipse_fitter = no');

% set sample rate in camera setup screen
Eyelink('command', 'sample_rate = %d',1000);

% set heuristic filter
Eyelink('command', 'heuristic_filter = 1 1');

% eye tracked
Eyelink('command', 'binocular_enabled = YES');
% Eyelink('command', 'active_eye = RIGHT');

% set parser (conservative saccade thresholds)
% Eyelink('command', 'saccade_velocity_threshold = 35');
% Eyelink('command', 'saccade_acceleration_threshold = 9500');

WaitSecs(.2);
