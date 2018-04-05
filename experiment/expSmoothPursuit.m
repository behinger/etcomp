function [] = expSmoothPursuit(win, screen_width, screen_height,eyetracking)
jumpsize = 0.2; % in s, the length of the smooth pursuit ramp

xCenter = screen_width/2;
yCenter = screen_height/2;

dir_degrees = linspace(0,360,24) % with 15 degrees
directions = dir_degrees(randperm(24));% randomly shuffled directions, in randomization though???

velocities = [16,18,20,22,24] % deg/s velocity
velocities_px = degToPix(velocities,60); % XXX
ifi = Screen('GetFlipInterval', win);


pd=makedist('Exponential','mu',500);
trunc_dist=truncate(pd,200,5000); % fixcross times

% random duration fix cross

% 
% v = 16; % deg / s
% vpx = degToPix(v,60); % pixel / s
% jumpsize = 0.2 * vpx;
% dir = 90; % in monitor coordinates
% 
% [dx,dy] = pol2cart(deg2rad(180 - dir),jumpsize)
% 
% 
% [endx,endy] = pol2cart(deg2rad(dir),degToPix(15,60))

for count= 1:10%size(pos,1)-1
    v = velocities_px(count);
    dir = directions(count);
    jumpsize = 0.2 * v;
    [dx,dy] = pol2cart(deg2rad(180 + dir),jumpsize);
    xstart = xCenter+dx;
    ystart = yCenter+dy;
    
    [dx,dy] = pol2cart(deg2rad(dir),degToPix(15,60));
    endx = dx+ xCenter;
    endy = dy+ yCenter;
    
    
    [vx,vy] = pol2cart(deg2rad(dir),v);
    distance= diff([xstart,ystart;endx,endy]);
    %stepsize = distance/(1.5*1/ifi);\
    stepsize = [vx, vy].*ifi;
    

    % get duration
    duration = random(trunc_dist)/1000; % in s
    
    % we want to start in the middle
    newPos = [xstart ystart];
    
    expDrawTarget(xCenter, yCenter,128,20,'fixcross', win);
    LastFlip =  flip_screen(screen_width,screen_height,win);
    KbWait()
    
    % start the trial
    expDrawTarget(xCenter, yCenter,128,20,'fixcross', win);
    LastFlip =  flip_screen(screen_width,screen_height,win);
    
    LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + duration); % image_fixcross_time = 0.5s
    sendETNotifications(eyetracking,requester,sprintf('FREEVIEW fixcross'))
    
    
    tic
    time = 0;%GetSecs;
    while ~KbCheck && ((time+ifi) < 15/velocities(count))

        newPos = round(newPos + stepsize);
%         newPos = [100-halfsize+gridPos,mid_y-halfsize,100+halfsize+gridPos,mid_y+halfsize]
%         stimRect = [0,0,size(marker,2),size(marker,1)];
        % TODO offset um halfsize
        
        expDrawTarget(newPos(1),newPos(2),[],1,'fixcross',win)
%         Screen('DrawTexture',win, stim, stimRect,);
        toc
        LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + (1 - 0.5) * ifi); % image_fixcross_time = 0.5s
        toc

         % Increment the time
        time = time + ifi;

    end
    WaitSecs(0.5)
    
end

