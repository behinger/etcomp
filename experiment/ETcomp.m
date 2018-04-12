% ET Comp experiment
%LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab

sca
clear all
%open screen
debug=false;
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
calibrate_eyelink = true;
calibrate_pupil = false;
requester = false;
if eyetracking == 1
    
    % Eyelink
    el = setup_eyelink(cfg.screen,cfg.small_grid_coord);
    %open log file
    Eyelink('OpenFile', sprintf('etc_s%03u.EDF',subject_id));          %CHANGE file name ?
    sessionInfo = sprintf('%s %s','SUBJECTINDEX',num2str(subject_id));
    Eyelink('message','METAEX %s',sessionInfo);
    
    % Pupillabs
    %     Pupil_started = input(sprintf('Has pupil capture been started an Manual Marker Calibration been selected? Check if Eyecam 1&2 are recorded! \n (1) - Confirm. \n >'));
    %     while Pupil_started ~= 1
    %         Pupil_started = input(sprintf('Has pupil capture been started an Manual Marker Calibration been selected? Check if Eyecam 1&2 are recorded! \n (1) - Confirm. \n >'));
    %     end
    try
        zmq_request('init');
    catch e
        fprintf(e.message)
        error('error starting zmq. Maybe forgot to start matlab using LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab, or maybe did not install zeromq?')
    end
    requester = zmq_request('add_requester', 'tcp://100.1.0.3:5004');
    requester = int32(requester);
    el.requester =requester;
    % Setup Eyelink
    Eyelink('StartSetup')
    
    
    % Start recording
    reply =sendETNotifications(eyetracking,requester,sprintf('R etc_s%03u',subject_id));
    
    
    
    if ~isnan(reply)
        fprintf('Pupil Labs Connected');
    end
    
    sendETNotifications(eyetracking,requester,'Connect Pupil');
end



%%
tic
for block = 1
    
    rand_block = select_randomization(cfg.rand, subject_id, block);
    
    % at the beginning of each block : calibrate ADD pupil labs
    if calibrate_eyelink
        fprintf('\n\nEYETRACKING CALIBRATION...')
              
        sendETNotifications(eyetracking,requester,sprintf('starting ET calib block %d',block));

        % start eyelink calibration
        local_EyelinkDoTrackerSetup(el)
        
        % stop pupil calibration
        
        fprintf('DONE\n\n')
    end
    
    [LastFlip] = Screen('Flip', cfg.screen.win);
    
    %% large grid
    expGuidedGrid(cfg.large_grid_coord,cfg.screen,rand_block.large, block,requester,eyetracking)
    
    %% Smooth pursuit
    expSmoothPursuit(cfg.screen,rand_block.smoothpursuit_speed,rand_block.smoothpursuit_angle, requester,eyetracking,block)
    
    %% free viewing
    cfg.freeviewing.randomization = rand_block.freeviewing;
    expShowImages('FREEVIEW',cfg.freeviewing, cfg.screen, requester, block, eyetracking)
    
    %% Microsaccades
    expMicrosaccades(cfg.screen, cfg.fixcross_time, eyetracking, requester, block)
    
    %% Blinks (beep)
    expPlayBeeps(cfg.screen,cfg.blink_number,block,requester,eyetracking)
    
    %% Pupil Dilation
    expPupilDilation(cfg.screen,rand_block.pupildilation, eyetracking, requester, block)
    
    %% Small Grid Before
    expGuidedGrid(cfg.small_grid_coord,cfg.screen,rand_block.smallBefore, block,requester,eyetracking);
    
    %% Yaw Head Motion
    expShowImages('YAW',cfg.yaw, cfg.screen, requester, block, eyetracking)
    
    %% Roll Head Motion
    expShowImages('ROLL',cfg.roll, cfg.screen, requester, block, eyetracking)
    
    %% Small Grid After
    expGuidedGrid(cfg.small_grid_coord,cfg.screen,rand_block.smallAfter, block,requester,eyetracking);
    
    %%
    toc
end

sendETNotifications(eyetracking,requester,'Finished Experiment');

sendETNotifications(eyetracking,requester,'r'); % stop pupillabs recording

Eyelink('StopRecording')

ShowCursor;
KbQueueRelease(cfg.keyboardIndex);
Screen('Close') %cleans up all textures
DrawFormattedText(cfg.screen.win, 'The experiment is complete! Thank you very much for your participation!', 'center', 'center',0, 60);
Screen('Flip', cfg.screen.win)

% save eyetracking data
if eyetracking==1 && calibrate_eyelink
    fulledffile = sprintf('data/etc_s%03u.EDF',subject_id);
    sendETNotifications('r',requester)
    zmq_request('close');
    Eyelink('CloseFile');
    Eyelink('WaitForModeReady', 500);
    Eyelink('ReceiveFile',sprintf('etc_s%03u.EDF',subject_id),fulledffile);
    Eyelink('WaitForModeReady', 500);
end
Eyelink('Shutdown')