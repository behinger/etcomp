function visual = prepScreens(const)
% 
% prepare screens for SpatStat 1
%
% version 1.0 - 28.05.13
%


% Choose screen with maximum id - the secondary display:
screenid = max(Screen('Screens'));
%screenid = min(Screen('Screens'));

% set resolution
visual=NearestResolution(screenid,[const.MoWide,const.MoHigh,const.MoFreq,const.MoPiSi]);
if ~ispc
    visual.oldRes=Screen('Resolution',screenid,visual.width,visual.height,visual.hz,visual.pixelSize,[]);
end

% Open a fullscreen onscreen window on that display, choose a background
% color of 128 = gray with 50% max intensity:
imagingMode = kPsychNeed32BPCFloat;
rect=[];
[visual.main,visual.rect] = Screen('OpenWindow', screenid, const.bgCol*255, rect, [], [], [], [], imagingMode);
visual.coor=CenterRect(const.coor,visual.rect);