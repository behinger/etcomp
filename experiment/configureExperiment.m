function [cfg] = configureExperiment()
resultpath='data/';
stimpath='stimuli/';
zmqpath = 'zmq/';
%addpath(genpath(stimpath)) 
addpath(genpath(zmqpath)) 
%addpath(genpath(resultpath)) %results path

% load randomizations
cfg= load([resultpath 'stimuli_randomization' '.mat']);
%cfg.image_randomization = rand.img;
%cfg.small_before_randomization = rand.smallBefore;
%cfg.small_after_randomization = rand.smallAfter;
%cfg.large_grid_randomization = rand.large;



% screen settings
whichScreen    = max(Screen('Screens')); 
mp = get(0, 'MonitorPositions'); %using  multiple screens
ScreenSize = mp(whichScreen+1,:);
ScreenSize(2) = 1;
cfg.background_color = 128;
screen_width = ScreenSize(3);
screen_height = ScreenSize(4);

[cfg.win, winRect] = Screen('OpenWindow',whichScreen,cfg.background_color,[0,0,screen_width,screen_height]);
cfg.images = loadImages(cfg.win);


% initial screen filling
Screen('FillRect', cfg.win, [cfg.background_color cfg.background_color cfg.background_color]);
cfg.screen_width = winRect(3);
cfg.screen_height = winRect(4);


% define constant stimulus variables
cfg.fixcross_time = 2;
cfg.image_time = 2;
cfg.image_width = 1500*0.8;
cfg.image_height = 1200*0.8% TODO make screen dependent
cfg.small_grid_coord = gridCoordinates(cfg.screen_width, cfg.screen_height, 13);
cfg.large_grid_coord = gridCoordinates(cfg.screen_width, cfg.screen_height, 49);
%settings

% attach keyboard
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices();
cfg.keyboardIndex=keyboardIndices(strcmp(productNames,'DELL Dell USB Entry Keyboard'));