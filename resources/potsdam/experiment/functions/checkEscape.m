function checkEscape(keyCode)
% abort Eyelink experiment by pressing ESC
%

if strcmp(KbName(keyCode),'esc')
    % cancel experiment
    Eyelink('Message','ExperimentTerminated');
    error=Eyelink('CheckRecording');
    if error==0
        Eyelink('StopRecording');
        WaitSecs(0.2);
    end
    Screen('CloseAll');
    error('Experiment terminated by user');
else 
    return;
end