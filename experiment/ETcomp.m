% ET Comp experiment
% Please start matlab using:
% LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab
% else the cosyzmq library will run into problems

%% Clean up
sca
clear all

% Debug mode allows transparent screen
debug=false;

%setup eyetracker
eyetracking=~debug; % variable whether eye tracking triggers, connections and calibratinos should be used
requester = ~debug; % similar, whether connection to pupil labs should be opened

if debug
    input('!!!!!!DEBUG MODE ON!!!!!!! Confirm with "Enter"');
    commandwindow;
    PsychDebugWindowConfiguration;
end                                                                                                                   
% set up path environment

cfg = expConfigure();
cfg.subject_id = input('\n subjectid: ');

% Initialize Sounddriver
InitializePsychSound(1);
%% Test Beep%%
fprintf('Test Beep\n');
dobeep = 1;
while dobeep
    testBeep()
    fprintf('\n')
    dobeep = ~input('Did you hear a beep (yes = 1/ no = 0)');
    fprintf('\n')
end

%% Eyetracking setup
if eyetracking == 1
    %% Eyelink
    %always start in the middle
    calibcoordinates = cfg.small_grid_coord;
    middlepoint = calibcoordinates(:,1) == 960 & calibcoordinates(:,2) == 540 ;
    calibcoordinates = calibcoordinates([find(middlepoint);find(~middlepoint)],:);
    el = setup_eyelink(cfg.screen,calibcoordinates);
    %open log file
    Eyelink('OpenFile', sprintf('etc_s%03u.EDF',cfg.subject_id));          %CHANGE file name ?
    sessionInfo = sprintf('%s %s','SUBJECTINDEX',num2str(cfg.subject_id));
    Eyelink('message','METAEX %s',sessionInfo);
    
    %% Pupil Labs
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
    Eyelink('StartSetup');
    
    % Start recording
    reply =    sendETNotifications(eyetracking,requester,'Connect Pupil');    
    
    if ~isnan(reply)
        fprintf('Pupil Labs Connected');
    else
        error('Pupil Labs not connected')
    end
    
end

%%
% Make the inital arangements
fprintf('\n ################# \n Make the inital arangements, no need to calibrate yet\n ##############\nc     ')
local_EyelinkDoTrackerSetup(el)

sendETNotifications(eyetracking,requester,sprintf('R etc_s%03u',cfg.subject_id));
showInstruction('BEGINNING',cfg.screen,requester,eyetracking,0)


for block = 1:6
    tic
    rand_block = select_randomization(cfg.rand, cfg.subject_id, block);
    
    % at the beginning of each block : calibrate 
    if eyetracking
        fprintf('\n\nEYETRACKING CALIBRATION...')
    
    
        % we need to stop eyelink to record the calibration
        Eyelink('StopRecording')
        
        sendETNotifications(eyetracking,requester,sprintf('starting ET calib block %d',block));
        
        
        % start both calibration
        
        local_EyelinkDoTrackerSetup(el)
        
        
        fprintf('DONE\n\n')
        
        Eyelink('StartRecording')
    end
    toc
    [LastFlip] = Screen('Flip', cfg.screen.win);
    
    %% large grid
    expGuidedGrid(cfg.large_grid_coord,cfg.screen,rand_block.large, block,requester,eyetracking)
    toc
    %% Smooth pursuit
    expSmoothPursuit(cfg.screen,rand_block.smoothpursuit_speed,rand_block.smoothpursuit_angle, requester,eyetracking,block)
    toc
    %% free viewing
    expShowImages('FREEVIEW',cfg.freeviewing, cfg.screen, requester, block, eyetracking, rand_block.freeviewing)
    toc
    %% Microsaccades
    expMicrosaccades(cfg.screen, cfg.fixcross_time, eyetracking, requester, block)
    toc
    %% Blinks (beep)
    expPlayBeeps(cfg.screen,cfg.blink_number,block,requester,eyetracking)
    toc
    %% Pupil Dilation
    expPupilDilation(cfg.screen,rand_block.pupildilation, eyetracking, requester, block)
    toc
    %% Small Grid Before
    expGuidedGrid(cfg.small_grid_coord,cfg.screen,rand_block.smallBefore, block,requester,eyetracking,'before');
    toc
    %% Condition shake/tilt
    expRotation(rand_block.firstmovement,cfg.screen, eyetracking, requester,rand_block, block); % give the whole randomization because it needs tilt + shake
    toc
    %
    %% Small Grid After
    expGuidedGrid(cfg.small_grid_coord,cfg.screen,rand_block.smallAfter, block,requester,eyetracking,'after');
    toc
    %
    %%
    
end

sendETNotifications(eyetracking,requester,'Finished Experiment');


DrawFormattedText(cfg.screen.win, 'The experiment is complete! Thank you very much for your participation!', 'center', 'center',0, 60);
Screen('Flip', cfg.screen.win)
save(sprintf('data/etc_s%03u.mat',cfg.subject_id), 'cfg')

% save eyetracking data
if eyetracking==1 
    % pupil labs
    sendETNotifications(eyetracking,requester,'r'); % stop pupillabs recording
    zmq_request('close');
    
    % eyelink
    Eyelink('StopRecording')
    fulledffile = sprintf('data/etc_s%03u.EDF',cfg.subject_id);
    Eyelink('CloseFile');
    Eyelink('WaitForModeReady', 500);
    Eyelink('ReceiveFile',sprintf('etc_s%03u.EDF',cfg.subject_id),fulledffile);
    Eyelink('WaitForModeReady', 500);

    
    Eyelink('Shutdown')


end

ShowCursor;
KbQueueRelease(cfg.keyboardIndex);
Screen('Close') %cleans up all textures

%% Save Datastructure

sca

