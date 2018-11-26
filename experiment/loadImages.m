function [freeviewing, yaw, roll,marker]= loadImages(win)
%% Image stimuli for freeviewing
% change to Image data path
stimpath='stimuli/';
addpath(genpath(stimpath))
dirData = dir('stimuli/Muster/*.jpg');
numberImages = size(dirData,1);
dirData={dirData.name};
freeviewing = nan(numberImages,length('f'));
% load all stimuli in folder
for count = 1:numberImages                           % ascending id
    
    IMG = imread([stimpath 'Muster/' dirData{count}]);
    
    % make and preload texture
    freeviewing(count)   = Screen('MakeTexture', win, IMG);
    [resident] = Screen('PreloadTextures', win, freeviewing(count,1));
end

%% Image stimuli for head yaw
dirDataYaw = dir('stimuli/Faces/*yaw.jpeg');
numberImages = size(dirDataYaw,1);
dirDataYaw={dirDataYaw.name};
yaw = nan(numberImages,length('f'));
for count = 1:numberImages                           % ascending id
    
    IMG = imread([stimpath 'Faces/' dirDataYaw{count}]);
    
    % make and preload texture
    yaw(count)   = Screen('MakeTexture', win, IMG);
    [resident] = Screen('PreloadTextures', win, yaw(count,1));
end

%% Image stimuli for head roll
dirDataRoll = dir('stimuli/Faces/*roll.jpg');
numberImages = size(dirDataRoll,1);
dirDataRoll={dirDataRoll.name};
roll = nan(numberImages,length('f'));
for count = 1:numberImages                           % ascending id
    
    IMG = imread([stimpath 'Faces/' dirDataRoll{count}]);
    
    % make and preload texture
    roll(count)   = Screen('MakeTexture', win, IMG);
    [resident] = Screen('PreloadTextures', win, roll(count,1));
end

%% Image stimuli for surface marker
dirDataMarker = dir('stimuli/surface*.png');
numberImages = size(dirDataMarker,1);
dirDataMarker={dirDataMarker.name};
marker = nan(numberImages,length('f'));
for count = 1:numberImages                           % ascending id
    
    
    IMG = imread([stimpath dirDataMarker{count}]);
    
    % make and preload texture
    marker(count)   = Screen('MakeTexture', win, IMG);
    [resident] = Screen('PreloadTextures', win, marker(count,1));
end
