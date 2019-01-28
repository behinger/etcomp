%% SpatStatmobil.m
%
% scene perception experiment
% - memorize scenes
% - structured vs. less structured images
%
% Only for use with mobile Eye Tracking Device
% Hans Trukenbrod & Lars Rothkegel
% Version 1, 21.01.2016
% Universität Potsdam

clear all;

%% pathes
pathFunc=[cd filesep 'functions'];
addpath(pathFunc);

%% experiment  
subject=[];
try
    %% get subject ID
    const=getID;
    
    %% check settings
     checkSettings(const);
    

    %% experimental setup
    const=allgVar(const);               % general variables
    trialinfo = genDesign(const);       % generate design
    visual = prepScreens(const);        % prepare screens; compute screen coordinates

    

    HideCursor; 
    %% final preparation
    % prepare variables
    [const]=finalPrepare(const,visual);
    
    
    % instructions
    dispInstructions('InsBegin.txt',const,visual);

    %% memorize images
    dispInstructions('InsMemo.txt',const,visual);
    [dummy]=memorizeImages(const,trialinfo,visual);
    subject.Mem=dummy;

    %% recall images
    dispInstructions('InsRecall.txt',const,visual);
    [dummy]=recallImages(const,trialinfo,visual);
    subject.Rec=dummy;
   
    
    %% acknowledgment
    dispInstructions('InsEnd.txt',const,visual);
catch
    lasterr
end

%% reset MATLAB & EYELINK
reddUp;
saveSubjectInfo(trialinfo,const,subject);
rmpath(pathFunc);