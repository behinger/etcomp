function []= guidedGrid(coords,screen_width,screen_height,win,subj,randomization, block)


eyetracking=false;

display_pos = coords(randomization,:)';


%%
background_color = 128;

%prepare a background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the background
lastflip = Screen('Flip', win);

%draw the first dot at the middle of the screen
draw_target(screen_width/2, screen_height/2,20,'fixcross', win);
%show the first marker
time =  flip_screen(screen_width,screen_height,win, lastflip);
%[time]=Screen('Flip', win);  %get the time of the current flip (when dot was shown)

if eyetracking==1
    Eyelink('message','TRIALID %d', 0);
    trialInfo = sprintf('%s %s','trial',num2str(0));
    Eyelink('message','METATR %s', trialInfo);
    Eyelink('StartRecording');
    Eyelink('WaitForModeReady', 100);
end
targetKey    ='Space';

%walk through the positions and show the circle
for count=1:size(display_pos,2)
    
    
    
    [answer rt]=waitForKB_linux(targetKey,time);
    
    if eyetracking  % send button press trigger
        send_trigger(213,eyetracking)
    end
    
    %draw the marker
    draw_target(display_pos(1,count), display_pos(2,count),20,'fixcross', win);
    %show the window with the current marker
    time =  flip_screen(screen_width,screen_height,win, lastflip);
    
    
    %     % safe every dot as single trial
    if eyetracking==1
        Eyelink('message','TRIALID %d', count);
        trialInfo = sprintf('%s %s','trial',num2str(count));
        Eyelink('message','METATR %s', trialInfo);
        Eyelink('StartRecording');
        Eyelink('WaitForModeReady', 100);
    end
end


[answer rt]=waitForKB_linux(targetKey,time);
if eyetracking  % send button press trigger
    send_trigger(213,eyetracking)
end
%show last dot in middle of screen
draw_target(screen_width/2, screen_height/2,20,'fixcross', win);

%[time]=Screen('Flip', win);
time =  flip_screen(screen_width,screen_height,win, lastflip);

[answer rt]=waitForKB_linux(targetKey,time);

if eyetracking  % send button press trigger
    send_trigger(213,eyetracking)
end
    
if eyetracking==1
    Eyelink('message','TRIALID %d', num_dots+1);
    trialInfo = sprintf('%s %s','trial',num2str(num_dots+1));
    Eyelink('message','METATR %s', trialInfo);
    Eyelink('StartRecording');
    Eyelink('WaitForModeReady', 100);
end

%prepare a clean background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the white background
time =  flip_screen(screen_width,screen_height,win, lastflip);

% Eyelink('StopRecording');

% add marker pos in the middle of the screen
display_pos = [display_pos,[screen_width/2;screen_height/2]];
save(['data/display_pos_' num2str(subj) '_' num2str(block) '_' num2str(size(display_pos,2)) '.mat'],'display_pos');


fprintf('\n Test finished.')


