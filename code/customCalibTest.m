function []= etCompCalibTest(screen_width,screen_height,win,ScreenSize,subj,num_dots, block)

% stimpath='/net/store/nbp/users/sitimm/nbp_intothewild/Documentation/pupil_calibration_marker_cutout';
%stimpath='/home/experiment/experiments/ET_Comp/experiment/pupil_calibration_marker_cutout';

stimpath='/net/store/nbp/users/iibs/ETComp/experiment/pupil_calibration_marker_cutout';
eyetracking=false;

percent=0.6;
lost=(1-percent)/2;
screen_width_right=screen_width-screen_width*lost;
screen_width_left=screen_width*lost;
screen_height_down=screen_height-screen_height*lost;
screen_height_up=screen_height*lost;

background_color = 128;

%half of the dot_size in pixels
%(minimum size proportional to manual marker calibration is 90 pixels ->
%halfsize=45
halfsize=20;

%pixel of spot in middle of screen
mid_x=screen_width/2;
mid_y=screen_height/2;

%how many dots are displayed? (best a square number as we compute a grid with the square root)
num_dots = 49;

%time that a marker is shown in seconds
markertime=1.8;


%% -----------------------   Load marker -------------------------- %

marker= imread([stimpath '.jpg']);

idx=find(marker>=150);
marker(idx)=128;

%%

stim   = Screen('MakeTexture', win, marker);


%% ----------------------- WL_FO:    Randomisation ------------------------- %

%per row and column we show as many dots as the square of the whole dot
%number
dots_per_row=sqrt(num_dots);

%calculate the coordinates of the dots on the x- and y-axis (equidistant)
x_coord=round(linspace(screen_width_left+halfsize,screen_width_right-halfsize,dots_per_row));
% x_coord=x_coord(2:end-1);
y_coord=round(linspace(screen_height_up+halfsize,screen_height_down-halfsize,dots_per_row));
% y_coord=y_coord(2:end-1);
[p,q] = meshgrid(x_coord, y_coord);
pairs = [p(:) q(:)];

% randomized positions
rand_dots=randperm(num_dots);
display_pos=pairs(rand_dots,:)';

%%


%prepare a background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the background
Screen('Flip', win);

%draw the first dot at the middle of the screen
Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[mid_x-halfsize,mid_y-halfsize,mid_x+halfsize,mid_y+halfsize]);
%show the first marker
[time]=Screen('Flip', win);  %get the time of the current flip (when dot was shown)

if eyetracking==1
    Eyelink('message','TRIALID %d', 0);
    trialInfo = sprintf('%s %s','trial',num2str(0));
    Eyelink('message','METATR %s', trialInfo);
    Eyelink('StartRecording');
    Eyelink('WaitForModeReady', 100);
end
targetKey    ='Space';

%walk through the positions and show the circle
for count=1:num_dots
    
    
    
    [answer rt]=waitForKB_linux(targetKey,time);
    
    if eyetracking  % send button press trigger
        send_trigger(213,eyetracking)
    end
    
    %draw the marker
    Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)], ...
        [display_pos(1,count)-halfsize,display_pos(2,count)-halfsize, ...
        display_pos(1,count)+halfsize,display_pos(2,count)+halfsize]);
    %show the window with the current marker
    [time]=Screen('Flip', win);
    
    
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
Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[mid_x-halfsize,mid_y-halfsize,mid_x+halfsize,mid_y+halfsize]);
[time]=Screen('Flip', win);
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
[time]=Screen('Flip', win,time+markertime);

% Eyelink('StopRecording');

% add marker pos in the middle of the screen
display_pos = [display_pos,[mid_x;mid_y]];                            
save(['/home/experiment/Desktop/experiments/ET_Comp/data/display_pos_' num2str(subj) '_' num2str(block) '.mat'],'display_pos');

fprintf('\n Test finished.')


