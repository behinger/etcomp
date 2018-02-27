function moving_dot(win, randomization,screen_width,screen_height)
stimpath='/net/store/nbp/users/iibs/ETComp/experiment/stimuli/pupil_calibration_marker_cutout';
percent=0.9;
lost=(1-percent)/2;
%pixel of spot in middle of screen
halfsize = 20;
mid_x=screen_width/2;
mid_y=screen_height/2;
marker= imread([stimpath '.jpg']);
idx=find(marker>=150);
marker(idx)=128;
stim   = Screen('MakeTexture', win, marker);
smaller=min(screen_width,screen_height);

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
background_color = 255;
%prepare a background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the background
lastflip = Screen('Flip', win);
ifi = Screen('GetFlipInterval', win);
amplitude = screen_height * 0.25;
% adapt frequenz
frequency = 0.2;
angFreq = 2 * pi * frequency;
startPhase = 0;
time = 0;
waitframes = 1;
gridPos = dots;
gridPos = dots(randperm(size(dots,1)),:);

for currPoint = 1:size(gridPos,1)-1
    time = 0;%GetSecs;
    newPos = gridPos(currPoint,:);
    
    distance= diff(gridPos(currPoint:(currPoint+1),:));
    stepsize = distance/(1.5*1/ifi);
    
    tic
    while ~KbCheck && ((time+ifi) < 1.5)

        newPos = newPos + stepsize;
%         newPos = [100-halfsize+gridPos,mid_y-halfsize,100+halfsize+gridPos,mid_y+halfsize]
%         stimRect = [0,0,size(marker,2),size(marker,1)];
        % TODO offset um halfsize
        
        draw_target(newPos(1),newPos(2),[],'fixcross',win)
%         Screen('DrawTexture',win, stim, stimRect,);
        lastflip  = Screen('Flip', win, lastflip + (1 - 0.5) * ifi);
         % Increment the time
        time = time + ifi;

    end
    WaitSecs(0.2)
    
end
%draw the first dot at the middle of the screen
