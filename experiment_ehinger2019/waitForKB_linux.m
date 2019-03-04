function [answer rt] = waitForKB_linux(targetkey,visual_onset)

%leftarrow = KbName('LeftArrow');
%rightarrow = KbName('RightArrow');
KbName('UnifyKeyNames');
while KbCheck; end % Wait until all keys are released.

if nargin < 2
    startSecs = GetSecs;
else
    startSecs=visual_onset;
end
answer=-1;

while 1
    % Check the state of the keyboard.
	[ keyIsDown, seconds, keyCode ] = KbCheck;
   
    % If the user is pressing a key, then display its code number and name.
    % 114 left 115 right
    if keyIsDown

        % Note that we use find(keyCode) because keyCode is an array.
        % See 'help KbCheck'
        %fprintf('You pressed key %i which is %s\n', find(keyCode), KbName(keyCode));

        if keyCode(KbName(targetkey))
            rt = seconds - startSecs;
            answer=1;
            break;
        end
        
        % If the user holds down a key, KbCheck will report multiple events.
        % To condense multiple 'keyDown' events into a single event, we wait until all
        % keys have been released.
        while KbCheck; end
    end
end

end
