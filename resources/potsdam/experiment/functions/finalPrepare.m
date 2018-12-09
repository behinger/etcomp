function [const]=finalPrepare(const,visual)
% finalize preparation of experiment


% fixation rectangle
const.fcHor = [0 0 const.fcL const.fcW];
const.fcVer = [0 0 const.fcW const.fcL];

% % blank screen
% Screen('FillRect', visual.main, const.bgCol*256, []);
% Screen('Flip', visual.main);


% call mex-files
GetSecs; KbCheck;
Snd('Play',sin(1:5));


