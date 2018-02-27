function []= calibrationPupilLabs(screen_width,screen_height,win,ScreenSize)

%

% stimpath='/home/experiment/experiments/ITW/WL_FO/pupil_calibration_marker_cutout';


stimpath='/net/store/nbp/users/iibs/ETComp/experiment/pupil_calibration_marker_cutout';



background_color = 255;


%% -----------------------   Load marker -------------------------- %

marker= imread([stimpath '.jpg']);
%%

stim   = Screen('MakeTexture', win, marker);



%% ----------------------- WL_FO:    Randomisation ------------------------- %


num_dots = 13;

%half of the dot_size in pixels
%(minimum size proportional to manual marker calibration is 90 pixels ->
%halfsize=45
halfsize=45;

percent=90;
percent_unused=100-percent;
%get the smaller of both screen dimensions and use this because then the
%distance between the marker and the screen border is the same on the x and
%the y axis (otherwise 95% of the pixels on the longer exis are more then
%95% on the smaller axis and therefor the marker will be closer to one
%border than the other)
smaller=min(screen_width,screen_height);

%pixel of spot in middle of screen
mid_x=screen_width/2;
mid_y=screen_height/2;

%pixels between outer spots and screen border
out_x=smaller*percent_unused/100;
out_y=smaller*percent_unused/100;

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


%prepare a white background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the white background
Screen('Flip', win);


%draw the first dot at the middle of the screen
Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[dots(1,1)-halfsize,dots(1,2)-halfsize,dots(1,1)+halfsize,dots(1,2)+halfsize]);
%show the first marker 
[time]=Screen('Flip', win);  %get the time of the current flip (when dot was shown)

%show the markers at all positions after each other (except for the middle of
%the screen -> only 12 positions
%compute a vector with randomized numbers from 1 to 12
numbers=[2:13];
randnumbers=numbers(randperm(length(numbers)));
%time that a marker is shown in seconds
markertime=1.8;
%walk through the positions and show the circle
for count=1:12
    %chose the current number in the vector of random numbers
    curr=randnumbers(count);
    %chose the spot (pixels of x and y location) that corresponds to the current number in the location
    %matrix
    spot(1)=dots(curr,1);
    spot(2)=dots(curr,2);
    
    %draw the marker
    Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[spot(1)-halfsize,spot(2)-halfsize,spot(1)+halfsize,spot(2)+halfsize]);
    %show the window with the marker 1 second after the last one
    [time]=Screen('Flip', win,time+markertime);
    
end

%show last dot in middle of screen
Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[dots(1,1)-halfsize,dots(1,2)-halfsize,dots(1,1)+halfsize,dots(1,2)+halfsize]);
[time]=Screen('Flip', win,time+markertime);

%prepare a white background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the white background
[time]=Screen('Flip', win,time+markertime);

fprintf('\n Calibration finished.')



