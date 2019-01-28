function [img,coor]=loadImage(const,visual,imgName)
% load image

%% read image
load(const.imgFile,imgName);
imgData=eval([imgName '.imgData']);
eval(['clear ' imgName;]);

%% make texture
coor = CenterRect([0 0 size(imgData,2) size(imgData,1)],visual.rect);
img = Screen('MakeTexture',visual.main,imgData);