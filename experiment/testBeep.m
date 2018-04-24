function [] = testBeep()

devs = PsychPortAudio('GetDevices');
%first USB device
devid = find(cellfun(@(x)~isempty(x),strfind({devs.DeviceName},'USB')),1);
pahandle = PsychPortAudio('Open',  devid, 1, 1, 48000, 2);
PsychPortAudio('Volume', pahandle, 1);
myBeep = MakeBeep(300, 0.1, 48000);

PsychPortAudio('FillBuffer', pahandle, [myBeep; myBeep]);

PsychPortAudio('Start', pahandle, 1, 0, 1);
[actualStartTime, ~, ~, estStopTime] = PsychPortAudio('Stop', pahandle, 1, 1);

% Close the audio device
PsychPortAudio('Close', pahandle);
