function [fix,ncal]=fixationCheck(const,el,visual,ncal,newCal,tr,x,y)
% fixation check
%

%% coordinates
fcHor=CenterRectOnPoint(const.fcHor,x,y);
fcVer=CenterRectOnPoint(const.fcVer,x,y);
fcArea=CenterRectOnPoint(const.fcArea,x,y);

%% Eyelink
% message
Eyelink('Message','CenterFixationCross %d %d %d',round(x),round(y),tr);
Eyelink('Message','FixationArea %d %d %d %d %d',fcArea(1),fcArea(2),fcArea(3),fcArea(4),tr);

% draw on operator screen, NB! eyetracker has to be offline!
Eyelink('Command','clear_screen 0');
Eyelink('Command','draw_box %d %d %d %d 15',fcArea(1),fcArea(2),fcArea(3),fcArea(4));
Eyelink('Command','record_status_message ''Fixationskontrolle, Trial %d''', tr);

% start recording eye position - record a few samples before you start displaying
Eyelink('StartRecording');
WaitSecs(0.2);
checkRecording(tr);

%% fixation check loop
nfix=0; fix=0;
while fix~=1
    % calibration
    if nfix>=const.nfix || ncal > newCal
        if ~const.EyelinkDummy
            Screen('FillRect',visual.main,const.bgCol*256,[]);
            Screen('Flip', visual.main);
            calibration(el);
        else
            Screen('FillRect',visual.main,const.bgCol*256,[]);
            Screen('Flip', visual.main);
            waitForResponse;
        end
        nfix=0; ncal=1;
        % start recording eye position
        Eyelink('StartRecording');
        WaitSecs(0.2);
        checkRecording(tr);
        clearBuffers;
    end
    nfix=nfix+1;
    
    % display fixation cross
    Screen('FillRect',visual.main,const.bgCol*256,[]);
    Screen('FillRect',visual.main,const.fcCol*256,fcHor);
    Screen('FillRect',visual.main,const.fcCol*256,fcVer);
    Screen('Flip', visual.main);
    
    % fixation check
    fix=checkFix(el,fcArea);
    if fix==1
        Eyelink('Message','FixationCheck %d %d',tr,nfix);
    end
    
    % cancel experiment?
    [keyIsDown, t2, keyCode]=KbCheck;
    checkEscape(keyCode);
end
