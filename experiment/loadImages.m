function [index]= loadImages(win)
%% Load image stimuli
% change to Image data path
stimpath='stimuli/';
addpath(genpath(stimpath)) 
dirData = dir('stimuli/Muster/*.jpg');
numberImages = size(dirData,1);
dirData={dirData.name};
index = nan(numberImages,length('f'));

% load all stimuli in folder
for id = 1:numberImages                           % ascending id
        
    IMG = imread([stimpath 'Muster/' dirData{id}]);
        
        
    % make and preload texture
    index(id)   = Screen('MakeTexture', win, IMG);
    [resident] = Screen('PreloadTextures', win, index(id,1));
        
    
end


