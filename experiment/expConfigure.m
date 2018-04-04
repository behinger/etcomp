function [cfg] = expConfigure()
resultpath='data/';
stimpath='stimuli/';
zmqpath = 'zmq/';
addpath(genpath(zmqpath))

% load randomizations
cfg = load([resultpath 'stimuli_randomization' '.mat']);

% screen settings
whichScreen    = max(Screen('Screens'));
mp = get(0, 'MonitorPositions'); %using  multiple screens
ScreenSize = mp(whichScreen+1,:);
ScreenSize(2) = 1;
cfg.background_color = 128;
screen_width = ScreenSize(3);
screen_height = ScreenSize(4);
[cfg.win, winRect] = Screen('OpenWindow',whichScreen,cfg.background_color,[0,0,screen_width,screen_height]);
[cfg.freeviewing.images cfg.yaw.images, cfg.roll.images] = loadImages(cfg.win);

% initial screen filling
Screen('FillRect', cfg.win, [cfg.background_color cfg.background_color cfg.background_color]);
cfg.screen_width = winRect(3);
cfg.screen_height = winRect(4);


% define constant stimulus variables
% microsaccades
cfg.fixcross_time = 2;

%  Number of blinks
cfg.blink_number = 7;
% freeviewing
cfg.freeviewing.image_width = 1500*0.8;
cfg.freeviewing.image_height = 1200*0.8% TODO make screen dependent
cfg.freeviewing.fixcross_time = 0.5;
cfg.freeviewing.image_time = 6;

% yaw
cfg.yaw.image_width = 570;
cfg.yaw.image_height = 594;
cfg.yaw.image_time = 6;

% roll
cfg.roll.image_width = 570;
cfg.roll.image_height = 594;
cfg.roll.image_time = 6;
cfg.surface_marker_size = 30;


% define grid coordinates
cfg.small_grid_coord = gridCoordinates(cfg.screen_width, cfg.screen_height,cfg.surface_marker_size , 13);
cfg.large_grid_coord = gridCoordinates(cfg.screen_width, cfg.screen_height,cfg.surface_marker_size , 49);

% attach keyboard
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices();
cfg.keyboardIndex=keyboardIndices(strcmp(productNames,'DELL Dell USB Entry Keyboard'));