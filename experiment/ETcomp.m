% ET Comp experiment
%LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab

sca
clear all
%open screen
debug=true;
if debug
    commandwindow;
    PsychDebugWindowConfiguration;
end
% set up path environment

cfg = expConfigure();

expName = input('\n \n WELCOME EXPERIMENTER! \n\n What is your name? \n >','s');
subject_id = input('\n subjectid: ');



% Initialize Sounddriver
InitializePsychSound(1);


%% Eyetracking setup
%setup eyetracker
eyetracking=1;
calibrate_eyelink = false;
calibrate_pupil = false;
requester = false;
if eyetracking == 1
    
    %EyelinkInit()
    %el = EyelinkInitDefaults(cfg.win);% win -> PTB window
    Pupil_started = input(sprintf('Has pupil capture been started an Manual Marker Calibration been selected? Check if Eyecam 1&2 are recorded! \n (1) - Confirm. \n >'));
    while Pupil_started ~= 1
        Pupil_started = input(sprintf('Has pupil capture been started an Manual Marker Calibration been selected? Check if Eyecam 1&2 are recorded! \n (1) - Confirm. \n >'));
    end
    try
    zmq_request('init');
    catch e
        fprintf(e.message)
        error('error starting zmq. Maybe forgot to start matlab using LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab, or maybe did not install zeromq?')
    end
    requester = zmq_request('add_requester', 'tcp://100.1.0.3:45697');
    requester = int32(requester);
    reply = sendETNotifications(eyetracking,requester,'Connect Pupil');
    sendETNotifications('R',requester)
    
    if ~isnan(reply)
        fprintf('Pupil Labs Connected');
    end
end

%setup eyelink
if eyetracking==1 && calibrate_eyelink == 1
    setup_eyetracker;
    %open log file
    Eyelink('OpenFile', sprintf('ETComp_s%u.EDF',subject_id));          %CHANGE file name ?
    sessionInfo = sprintf('%s %s','SUBJECTINDEX',num2str(subject_id));
    Eyelink('message','METAEX %s',sessionInfo);
    sendETNotifications(sprintf('R ETComp_s%u.EDF',subject_id),requester)
    
    %send first triggers
    send_trigger(0,eyetracking);
    send_trigger(200,eyetracking);
    
end

%%
% for block = 1:6
block = 1;
rand_block = select_randomization(cfg.rand, subject_id, block);
cfg.freeviewing.randomization = rand_block.freeviewing;
% at the beginning of each block : calibrate ADD pupil labs
if calibrate_eyelink
    fprintf('\n\nEYETRACKING CALIBRATION...')
    
    EyelinkDoTrackerSetup(el);
    fprintf('DONE\n\n')
end

if calibrate_pupil
    fprintf('\n\nEYETRACKING CALIBRATION...')
    
    sendETNotifications('notify',requester)
    fprintf('DONE\n\n')
end
[LastFlip] = Screen('Flip', cfg.win);

%% large grid
expGuidedGrid(cfg.large_grid_coord,cfg.screen_width,cfg.screen_height,cfg.win,rand_block.large, block,requester,eyetracking)

%% Smooth pursuit
expSmoothPursuit(cfg.win, cfg.screen_width, cfg.screen_height)
%% free viewing
expShowImages('freeviewing',cfg.freeviewing, cfg.screen_width, cfg.screen_height, cfg.win, requester, block, eyetracking)

%% Microsaccades
expMicrosaccades(cfg.win, cfg.screen_width, cfg.screen_height, cfg.fixcross_time, eyetracking, requester, block)

%% Blinks (beep)
expPlayBeeps(cfg.blink_number,block,requester,eyetracking)

%% Pupil Dilation
expPupilDilation(cfg.win,cfg.screen_width,cfg.screen_height,rand_block.pupildilation, eyetracking, requester, block)

%% Small Grid Before
expGuidedGrid(cfg.small_grid_coord,cfg.screen_width,cfg.screen_height,cfg.win,rand_block.smallBefore, block,requester,eyetracking);

%% Yaw Head Motion
expShowImages('yaw',cfg.yaw, cfg.screen_width, cfg.screen_height, cfg.win, requester, block, eyetracking)

%% Roll Head Motion
expShowImages('roll',cfg.roll, cfg.screen_width, cfg.screen_height, cfg.win, requester, block, eyetracking)

%% Small Grid After
expGuidedGrid(cfg.small_grid_coord,cfg.screen_width,cfg.screen_height,cfg.win,rand_block.smallAfter, block,requester,eyetracking);

%%
if eyetracking  % send experiment end trigger
    send_trigger(255,eyetracking)
end

               
ShowCursor;
KbQueueRelease(cfg.keyboardIndex);
Screen('Close') %cleans up all textures
DrawFormattedText(cfg.win, 'The experiment is complete! Thank you very much for your participation!', 'center', 'center',0, 60);
Screen('Flip', cfg.win)

% save eyetracking data
if eyetracking==1 && calibrate_eyelink
    fulledffile = sprintf('%s.EDF',outputname);
    sendETNotifications('r',requester)
    zmq_request('close');
    Eyelink('CloseFile');
    Eyelink('WaitForModeReady', 500);
    Eyelink('ReceiveFile',sprintf('ETComp_s%u.EDF',subject_id),fulledffile);
    Eyelink('WaitForModeReady', 500);
end