function el = setup_eyelink(screen,calib_coords)
%fetch the Eyetracker
if EyelinkInit()~= 1
    return;
end;
%initialize with defaults, tell the Eyetracking on what screen to draw
el=EyelinkInitDefaults(screen.win);

% ETCOMP SPECIALYTZ
el.screen = screen;

Eyelink('command', 'enable_automatic_calibration = YES'); %automatic calibration

screenInfo = sprintf('screen_pixel_coords = 0 0 %d %d',screen.screen_width,screen.screen_height);
Eyelink('command',screenInfo);
screenInfo = sprintf('screen_phys_coords = -266 149 266 -149'); %physical screen size: BENQ XL 2420 T 531mm x 299mm
%screenInfo = sprintf('screen_phys_coords = -358 202 358 -202'); %physical screen size: Asus
Eyelink('command',screenInfo);
prescale = sprintf('screen_write_prescale=4');
Eyelink('command',prescale);
remote_position = sprintf('remote_camera_position -10 10 32 -40 -225');
display('XXX CHECK THIS')
Eyelink('command',remote_position);

% make sure that we get gaze data from the Eyelink and that we have the
% right information in the EDF file
Eyelink('command', 'link_sample_data = LEFT,RIGHT,GAZE,AREA,GAZERES,HREF,PUPIL,STATUS');
Eyelink('command', 'link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON');
Eyelink('command', 'link_sample_filter = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS');

Eyelink('command', 'file_sample_data = LEFT,RIGHT,GAZE,AREA,GAZERES,HREF,PUPIL,STATUS');
Eyelink('command', 'file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON');
Eyelink('command', 'file_sample_filter = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS');


% set parser (conservative saccade thresholds)
Eyelink('command', 'select_parser_configuration = 0');

el.calibrationtargetsize=0.6; %the larger this is, the larger the overall calibration target
el.calibrationtargetwidth=0.1; %the larger this number, the smaller the white dot in the center




EyelinkUpdateDefaults(el);
% 
%%%%%%%%%% set eyelink calibration %%%%%%%%%%%%%%
% Calibration
% overwrite tracker config
Eyelink('command', 'calibration_type = HV13');
Eyelink('command', 'validation_type = HV13');
Eyelink('command','generate_default_targets = YES');

calib = sprintf('%d,%d ',calib_coords');
Eyelink('command',sprintf('calibration_targets = %s',calib));
Eyelink('command',sprintf('validation_targets = %s',calib));

