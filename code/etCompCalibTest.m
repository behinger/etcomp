function []= etCompCalibTest(screen_width,screen_height,win,ScreenSize,subj,num_dots,randomization, block)

% stimpath='/net/store/nbp/users/sitimm/nbp_intothewild/Documentation/pupil_calibration_marker_cutout';
%stimpath='/home/experiment/experiments/ET_Comp/experiment/pupil_calibration_marker_cutout';

stimpath='/net/store/nbp/users/iibs/ETComp/experiment/stimuli/pupil_calibration_marker_cutout';
eyetracking=false;

percent=0.9;
lost=(1-percent)/2;
%pixel of spot in middle of screen
mid_x=screen_width/2;
mid_y=screen_height/2;

%get the smaller of both screen dimensions and use this because then the
%distance between the marker and the screen border is the same on the x and
%the y axis (otherwise 95% of the pixels on the longer exis are more then
%95% on the smaller axis and therefor the marker will be closer to one
%border than the other)
smaller=min(screen_width,screen_height);

background_color = 128;

%half of the dot_size in pixels
%(minimum size proportional to manual marker calibration is 90 pixels ->
%halfsize=45
halfsize=20;

%time that a marker is shown in seconds
markertime=1.8;


%% -----------------------   Load marker -------------------------- %

marker= imread([stimpath '.jpg']);

idx=find(marker>=150);
marker(idx)=128;

%%

stim   = Screen('MakeTexture', win, marker);


%% ----------------------- WL_FO:    Randomisation ------------------------- %
if num_dots == 49
    screen_width_right=screen_width-screen_width*lost;
    screen_width_left=screen_width*lost;
    screen_height_down=screen_height-screen_height*lost;
    screen_height_up=screen_height*lost;
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

    % randomized positions - ADD custom randomisation
    %rand_dots=randperm(num_dots);
    %display_pos=pairs(rand_dots,:)';
    display_pos=pairs(randomization,:)';
elseif num_dots == 13


    %pixels between outer spots and screen border
    out_x=smaller*lost;
    out_y=smaller*lost;

    %pixel between inner spots and screen border
    in_x=out_x+((mid_x-out_x)/2);
    in_y=out_y+((mid_y-out_y)/2);
    dots=[];
    % spot at middle of the screen in pixels for x_axis
    dots(1,1)=mid_x;
    % spot at middle of the screen in pixels for y_axis
    dots(1,2)=mid_y;
    %spot in upperleft corner
    dots(2,1)=out_x;
    dots(2,2)=out_y;
    %left side middle
    dots(3,1)=out_x;
    dots(3,2)=mid_y;
    %lower left corner
    dots(4,1)=out_x;
    dots(4,2)=screen_height-out_y;
    %upper right corner
    dots(5,1)=screen_width-out_x;
    dots(5,2)=out_y;
    %right side middle
    dots(6,1)=screen_width-out_x;
    dots(6,2)=mid_y;
    %lower right corner
    dots(7,1)=screen_width-out_x;
    dots(7,2)=screen_height-out_y;
    %inner upper left
    dots(8,1)=in_x;
    dots(8,2)=in_y;
    %inner lower left
    dots(9,1)=in_x;
    dots(9,2)=screen_height-in_y;
    %inner upper right
    dots(10,1)=screen_width-in_x;
    dots(10,2)=in_y;
    %inner lower right
    dots(11,1)=screen_width-in_x;
    dots(11,2)=screen_height-in_y;
    %upper middle
    dots(12,1)=mid_x;
    dots(12,2)=out_y;
    %lower middle
    dots(13,1)=mid_x;
    dots(13,2)=screen_height-out_y;
    % ADD custom randomisation
    %numbers=[2:13];
    %randnumbers=numbers(randperm(length(numbers)));
    %rand_dots=randperm(num_dots);
    display_pos=dots(randomization,:)';
end

%%


%prepare a background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the background
lastflip = Screen('Flip', win);

%draw the first dot at the middle of the screen
Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[mid_x-halfsize,mid_y-halfsize,mid_x+halfsize,mid_y+halfsize]);
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
Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[mid_x-halfsize,mid_y-halfsize,mid_x+halfsize,mid_y+halfsize]);
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

%[time]=Screen('Flip', win,time+markertime);

% Eyelink('StopRecording');

% add marker pos in the middle of the screen
display_pos = [display_pos,[mid_x;mid_y]];
save(['/net/store/nbp/users/iibs/ETComp/data/display_pos_' num2str(subj) '_' num2str(block) '_' num2str(num_dots) '.mat'],'display_pos');

%save(['/home/experiment/Desktop/experiments/ET_Comp/data/display_pos_' num2str(subj) '_' num2str(block) '_' num2str(num_dots) '.mat'],'display_pos');

fprintf('\n Test finished.')


