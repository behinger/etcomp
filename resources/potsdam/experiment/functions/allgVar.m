function const = allgVar(const)
%
% experimental settings of SpatStat experiment
%
% version 1.0 - 28.05.13
%


%% setup
const.MoWide = 1280;
const.MoHigh = 1024;
const.MoFreq = 60;
const.MoPiSi = 32;

%% display image
const.Boundary=0.03125;      % frame around image 
const.BoundaryX=const.MoWide*const.Boundary;
const.BoundaryY=const.MoHigh*const.Boundary;
const.coor=[0 0 const.MoWide const.MoHigh]+[const.BoundaryX const.BoundaryY -const.BoundaryX -const.BoundaryY];
const.bgCol  = [1 1 1];   % background color 
const.imgFile=['imgs' filesep 'ImagesSpatStat.mat']; % image mat file 

%% memorization
const.MinDurPause = 1;       % minimum pause duration between trials
const.PresTime = 10;         % presentation time
const.repImgs=2;             % repeat presentation


%% random number
const.SEED=654998113+const.vpnr;  % set seed
rand('twister',const.SEED);

%% recall images
const.keyCorr='right';
const.keyFalse='left';

%% Calibration Check
const.LeftBig= [185 457 295 567];
const.LeftSmall= [230 502 250 522];


const.UpBig= [865 737 975 847];
const.UpSmall= [910  782  930  802];


const.DownBig= [585 57 695 167];
const.DownSmall= [630 102 650 122];

const.calcol=[0 0 0];
const.calcol2=[1 1 1];
const.ncalMem=9;
const.ncalRec=20;

%% Fixation Cross
const.fcL = 19;             % length fixation cross
const.fcW = 3;
const.fcx = const.MoWide/2;			% X-Axis Location of Fixation Cross, Partition of Screen 
const.fcy=const.MoHigh/2;   %Y-Axis locaion of Fixation Cross
const.fcCol=[1 1 1];

%% sounds
[const.beep,samplingRate]    = MakeBeep(200,.5,[1000]);
[const.beepRT,samplingRate]  = MakeBeep(300,2.5,[1500]);

%Presentation Time Background
const.CheckTime=1;
