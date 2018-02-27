% ET Comp experiment
sca
%open screen
debug=true;
if debug
    commandwindow;
    PsychDebugWindowConfiguration;
end
% set up path environment
exppath='/net/store/nbp/users/iibs/ETComp/experiment/';
resultpath='/net/store/nbp/users/iibs/ETComp/data/';
stimpath='/net/store/nbp/users/iibs/ETComp/experiment/stimuli/';
randomizations = load([resultpath 'stimuli_randomization' '.mat']);
img_random = randomizations.rand.img;
addpath(genpath(stimpath)) 
addpath(genpath(resultpath)) %results path

%settings

expName = input('\n \n WELCOME EXPERIMENTER! \n\n What is your name? \n >','s');
subject_id = input('\n subjectid: ');
%subject_id = 1
%background_color = 255;                                     %CHECK if correct!

% screen settings
whichScreen    = max(Screen('Screens'));
mp = get(0, 'MonitorPositions'); %using  multiple screens
ScreenSize = mp(whichScreen+1,:);
ScreenSize(2) = 1;
background_color = 255;
[win, winRect] = Screen('OpenWindow',whichScreen,background_color,[0,0,ScreenSize(3),ScreenSize(4)]);


% initial screen filling
Screen('FillRect', win, [background_color background_color background_color]);
screen_width = winRect(3);
screen_height = winRect(4);


% attach keyboard
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices();
keyboardIndex=keyboardIndices(strcmp(productNames,'DELL Dell USB Entry Keyboard'));
%% Load image stimuli
% change to Image data path
cd '/net/store/nbp/users/iibs/ETComp/experiment/stimuli/Muster/'
dirData = dir('*.jpg');
dirData={dirData.name};
stimID = 1:15; % change depending on how many stimuli needed
for id = 1:length(stimID)                             % ascending id
        
    IMG = imread([stimpath 'Muster/' dirData{id}]);
        
        
    % make and preload texture
    index(id)   = Screen('MakeTexture', win, IMG);
    Screen('PreloadTextures', win, index(id));
        
    
end

% why???
cd(exppath)


%% Eyetracking setup
%setup eyetracker
eyetracking=false;
calibrate_eyelink = false;

if eyetracking == 1
    EyelinkInit()
    el = EyelinkInitDefaults(win);% win -> PTB window
end

%setup eyelink
if eyetracking==1
    setup_eyetracker;
    %open log file
    Eyelink('OpenFile', sprintf('ETComp_s%u.EDF',subject_id));          %CHANGE file name ?
    sessionInfo = sprintf('%s %s','SUBJECTINDEX',num2str(subject_id));
    Eyelink('message','METAEX %s',sessionInfo);
    
    %send first triggers
    send_trigger(0,eyetracking);
    send_trigger(200,eyetracking);
    
end
%%

block = 1;
% at the beginning of each block : calibrate ADD pupil labs
if calibrate_eyelink
    fprintf('\n\nEYETRACKING CALIBRATION...')
    EyelinkDoTrackerSetup(el);
    fprintf('DONE\n\n')
end
[LastFlip] = Screen('Flip', win);

% large grid
%etCompCalibTest(screen_width,screen_height,win,ScreenSize,subject_id,49,randomizations.rand.big,block);
% smooth pursuit
WaitSecs(0.1)
moving_dot(win, randomizations.rand.small,screen_width,screen_height)
% free viewing
% define size of image
image_size = 0.8; % scaling factor, make screen dependend TODO
image_width = size(IMG,2)*image_size;
image_height = size(IMG,1)* image_size;
% % display random images
for id = 1+3*(block-1):3+3*(block-1)
     draw_target(screen_width/2, screen_height/2,20,'fixcross', win);
     LastFlip = flip_screen(screen_width,screen_height,win,0);
    
     displayPos =[screen_width/2-image_width/2,screen_height/2-image_height/2,screen_width/2+image_width/2,screen_height/2+image_height/2];
     Screen('DrawTexture',win, index(img_random(id)), [0,0,size(IMG,2),size(IMG,1)],[displayPos]);

     LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + 0.5);  
     LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + 2);
     

%      pause(2) % show stimulus for certain time
end
%%
% % fixation cross
% xCenter = screen_width/2; %in px
% yCenter = screen_height/2;
% whichTarget = 'fixcross';
% draw_target(xCenter,yCenter,20,whichTarget, win);
% LastFlip = flip_screen(screen_width,screen_height,win, LastFlip);
% pause(2) % what about screen correction time?
% blinks (beep)
% pupil dilation
% small grid
etCompCalibTest(screen_width,screen_height,win,ScreenSize,subject_id,13,randomizations.rand.small,block);

% yaw head motion
% roll
% small grid
%etCompCalibTest(screen_width,screen_height,win,ScreenSize,subject_id,49,randomizations.rand.small,block);




%%
if eyetracking  % send experiment end trigger
    send_trigger(255,eyetracking)
end


ShowCursor;
KbQueueRelease(keyboardIndex)
Screen('Close') %cleans up all textures
DrawFormattedText(win, 'The experiment is complete! Thank you very much for your participation!', 'center', 'center',0, 60);
Screen('Flip', win)



% save eyetracking data
if eyetracking==1 && calibrate_eyelink
    fulledffile = sprintf('%s.EDF',outputname);
    Eyelink('CloseFile');
    Eyelink('WaitForModeReady', 500);
    Eyelink('ReceiveFile',sprintf('ETComp_s%u.EDF',subject_id),fulledffile);
    Eyelink('WaitForModeReady', 500);
end