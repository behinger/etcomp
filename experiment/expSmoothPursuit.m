function [] = expSmoothPursuit(win, screen_width, screen_height)

xCenter = screen_width/2;
yCenter = screen_height/2;

dir_degrees = linspace(0,360,24) % with 15 degrees
directions = dir_degrees(randperm(24)); % randomly shuffled directions, in randomization though???

velocities = [16,18,20,22,24] % deg/s velocity

pd=makedist('Exponential','mu',700);
trunc_dist=truncate(pd,200,5000); % fixcross times

% random duration fix cross
duration = random(trunc_dist)
LastFlip =  flip_screen(screen_width,screen_height,win)
expDrawTarget(xCenter, yCenter,128,20,'fixcross', win);
LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + duration); % image_fixcross_time = 0.5s
sendETNotifications(eyetracking,requester,sprintf('FREEVIEW fixcross'))



for currPoint = 1:size(pos,1)-1
    time = 0;%GetSecs;
    newPos = pos(currPoint,:);
    
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

function [ppd] = pixelsPerDegree(screen_width, screen_height,distance)

ppd =  2* distance * resolution 
