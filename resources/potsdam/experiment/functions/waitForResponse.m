function [keyCode t2 Mx My Mb]=waitForResponse
% wait for mouse button
%
% keyCode - key code
% t       - time
% Mx      - x position
% My      - y position
% Mb      - button
%

clearBuffers; keyIsDown=0; Mb=0;
while ~keyIsDown & all(Mb==0)
    [keyIsDown, t2, keyCode] = KbCheck;
    [Mx, My, Mb]=GetMouse;
end
checkEscape(keyCode);