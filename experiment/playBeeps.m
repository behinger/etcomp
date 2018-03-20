function [] = playBeeps()
nrchannels = 2;
freq = 48000;
waitForDeviceStart = 1;
% How many times to we wish to play the sound
repetitions = 1;
% Length of the beep
beepLengthSecs = 0.1;
% Length of the pause between beeps
beepPauseTime = 1.5;

pahandle = PsychPortAudio('Open', [], 1, 1, freq, nrchannels);
PsychPortAudio('Volume', pahandle, 0.2);

myBeep = MakeBeep(400, beepLengthSecs, freq);
startCue = 0;
PsychPortAudio('FillBuffer', pahandle, [myBeep; myBeep]);
for beep = 1:8
    PsychPortAudio('Start', pahandle, repetitions, startCue, waitForDeviceStart);
    [actualStartTime, ~, ~, estStopTime] = PsychPortAudio('Stop', pahandle, 1, 1);

    % Compute new start time for follow-up beep, beepPauseTime after end of
    % previous one
    startCue = estStopTime + beepPauseTime;


end
% Close the audio device
PsychPortAudio('Close', pahandle);