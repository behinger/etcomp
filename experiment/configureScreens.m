function [cfg] = configureExperiment()
resultpath='data/';
stimpath='stimuli/';
addpath(genpath(stimpath)) 
addpath(genpath(resultpath)) %results path

load([resultpath 'stimuli_randomization' '.mat']);
cfg.image_randomization = rand.img;
cfg.small_grid_randomization = rand.small;
cfg.large_grid_randomization = rand.large;
cfg.surface_marker_size = 30;
%settings

% screen settings
whichScreen    = max(Screen('Screens')); 
mp = get(0, 'MonitorPositions'); %using  multiple screens
ScreenSize = mp(whichScreen+1,:);
ScreenSize(2) = 1;
cfg.background_color = 128
screen_width = ScreenSize(3)
screen_height = ScreenSize(4)

[cfg.win, winRect] = Screen('OpenWindow',whichScreen,cfg.background_color,[0,0,screen_width,screen_height]);


% initial screen filling
Screen('FillRect', cfg.win, [cfg.background_color cfg.background_color cfg.background_color]);
cfg.screen_width = winRect(3);
cfg.screen_height = winRect(4);

% attach keyboard
[keyboardIndices, productNames, allInfos] = GetKeyboardIndices();
keyboardIndex=keyboardIndices(strcmp(productNames,'DELL Dell USB Entry Keyboard'));