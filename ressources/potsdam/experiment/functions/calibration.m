function calibresult = calibration(el)
% calibrate eyes - experiment SpatStat
%
%

if Eyelink('isconnected') == el.connected
	HideCursor;
end

Snd('Play',el.beep);
WaitSecs(.2);

calibresult = EyelinkDoTrackerSetup(el,'c');

EyelinkSetup;
