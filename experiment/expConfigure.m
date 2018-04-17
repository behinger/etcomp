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
cfg.screen.background_color = 128;
screen_width = ScreenSize(3);
screen_height = ScreenSize(4);
[cfg.screen.win, winRect] = Screen('OpenWindow',whichScreen,cfg.screen.background_color,[0,0,screen_width,screen_height]);
[cfg.freeviewing.images cfg.yaw.images, cfg.roll.images,cfg.screen.surface_marker] = loadImages(cfg.screen.win);

% initial screen filling
Screen('FillRect', cfg.screen.win, [cfg.screen.background_color cfg.screen.background_color cfg.screen.background_color]);
cfg.screen.screen_width = winRect(3);
cfg.screen.screen_height = winRect(4);


% define constant stimulus variables
% microsaccades
cfg.fixcross_time = 20;

%  Number of blinks
cfg.blink_number = 7;
% freeviewing
cfg.freeviewing.image_width = 1500*0.6;
cfg.freeviewing.image_height = 1200*0.6;% TODO make screen dependent
cfg.freeviewing.fixcross_time = 0.8;
cfg.freeviewing.image_time = 6;

% yaw
cfg.yaw.image_width = 570;
cfg.yaw.image_height = 594;
cfg.yaw.image_time = 6;

% roll
cfg.roll.image_width = 570;
cfg.roll.image_height = 594;
cfg.roll.image_time = 6;
cfg.screen.surface_marker_size = 75; % change also in flip Screen
cfg.screen.color_condition_begin = [85,107,47];

% define grid coordinates
cfg.small_grid_coord = gridCoordinates(screen_width, screen_height,cfg.screen.surface_marker_size , 13);
cfg.large_grid_coord = gridCoordinates(screen_width, screen_height,cfg.screen.surface_marker_size , 49);

% attach keyboard
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices();
cfg.keyboardIndex=keyboardIndices(strcmp(productNames,'DELL Dell USB Entry Keyboard'));