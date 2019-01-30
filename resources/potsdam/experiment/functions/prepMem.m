function trialok=prepTrial(visual,coor,tr,ntr,task)
% prepare trial

% clear screen
Screen('FillRect',visual.main,[0 0 0],[]);
Screen('Flip',visual.main);

% pause recording eye position
Eyelink('SetOfflineMode');
WaitSecs(0.2);

% drawings on operator screen, NB! eyetracker has to be offline!
Eyelink('Command','clear_screen 0');
Eyelink('Command','draw_box %d %d %d %d 15',coor(1),coor(2),coor(3),coor(4));
Eyelink('Command','record_status_message ''%sTrial %d von %d''', task,tr,ntr);

% start recording eye position
Eyelink('StartRecording');
WaitSecs(0.2);
trialok=checkRecording(tr);