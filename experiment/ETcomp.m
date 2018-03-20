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

cfg = configureExperiment();
       
expName = input('\n \n WELCOME EXPERIMENTER! \n\n What is your name? \n >','s');
subject_id = input('\n subjectid: ');



% Initialize Sounddriver
InitializePsychSound(1);


%% Eyetracking setup
%setup eyetracker
eyetracking=true;
calibrate_eyelink = false;
calibrate_pupil = true;
if eyetracking == 1
    %EyelinkInit()
    %el = EyelinkInitDefaults(cfg.win);% win -> PTB window
    Pupil_started = input(sprintf('Has pupil capture been started an Manual Marker Calibration been selected? Check if Eyecam 1&2 are recorded! \n (1) - Confirm. \n >'));
while Pupil_started ~= 1
    Pupil_started = input(sprintf('Has pupil capture been started an Manual Marker Calibration been selected? Check if Eyecam 1&2 are recorded! \n (1) - Confirm. \n >'));
end
    zmq_request('init');
    requester = zmq_request('add_requester', 'tcp://localhost:50020');
    requester = int32(requester);
    reply = sendETNotifications('Connect Pupil', requester);
    sendETNotifications('R',requester)

    if ~isnan(reply)
        fprintf('Pupil Labs Connected');
    end
end

%setup eyelink
if eyetracking==1 & calibrate_eyelink == 1
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
rand = select_randomization(cfg.rand, subject_id, block);
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

% large grid
%guidedGrid(cfg.large_grid_coord,cfg.screen_width,cfg.screen_height,cfg.win,subject_id,rand.large, block)% smooth pursuit
WaitSecs(0.1);
%moving_dot(cfg.win,
%cfg.small_grid_randomization,cfg.screen_width,cfg.screen_height);
% free viewing
% define size of image

% % display random images
for id = 1:3

     draw_target(cfg.screen_width/2, cfg.screen_height/2,20,'fixcross', cfg.win);
     LastFlip = flip_screen(cfg.screen_width,cfg.screen_height,cfg.win,0);
    
     displayPos =[cfg.screen_width/2-cfg.image_width/2,cfg.screen_height/2-cfg.image_height/2,cfg.screen_width/2+cfg.image_width/2,cfg.screen_height/2+cfg.image_height/2];
     Screen('DrawTexture',cfg.win,cfg.images(rand.freeviewing(id)), [0,0,cfg.image_width,cfg.image_height],[displayPos]);

     LastFlip = flip_screen(cfg.screen_width,cfg.screen_height,cfg.win, LastFlip + 0.5);  
     LastFlip = flip_screen(cfg.screen_width,cfg.screen_height,cfg.win, LastFlip + 2);
     

   %   pause(2) 
% show stimulus for certain time
end
%%
% % fixation cross
%draw_target(cfg.screen_width/2, cfg.screen_height/2,20,'fixcross', cfg.win);
%LastFlip = flip_screen(cfg.screen_width,cfg.screen_height,cfg.win, LastFlip);
%pause(2) % what about screen correction time?

% blinks (beep)
%playBeeps()

% pupil dilation
for color_id = 1:25
Screen('FillRect', cfg.win, [rand.pupildilation(color_id) rand.pupildilation(color_id) rand.pupildilation(color_id)]);
LastFlip = flip_screen(cfg.screen_width,cfg.screen_height,cfg.win, LastFlip + 2);  

end
% small grid
guidedGrid(cfg.small_grid_coord,cfg.screen_width,cfg.screen_height,cfg.win,subject_id,rand.smallBefore, block);% smooth pursuit

% yaw head motion
% roll
% small grid
%guidedGrid(cfg.small_grid_coord,cfg.screen_width,cfg.screen_height,cfg.win,subject_id,rand.smallAfter, block)% smooth pursuit

%end


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