function [] = expSmoothPursuit(screen,velocities,directions,requester,eyetracking,block)
showInstruction('SMOOTHPURSUIT',screen,requester,eyetracking, block);

jumpsize = 0.2; % in s, the length of the smooth pursuit ramp

xCenter = screen.screen_width/2;
yCenter = screen.screen_height/2;

dir_degrees = linspace(0,360,24); % with 15 degrees
%directions = dir_degrees(randperm(24));% randomly shuffled directions, in randomization though???

%velocities = [16,18,20,22,24] % deg/s velocity
% velocities_px = degToPix(velocities,60); % XXX
ifi = Screen('GetFlipInterval', screen.win);


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
sendETNotifications(eyetracking,requester,sprintf('SMOOTH PURSUIT start, block %d', block))

for count= 1:length(directions)%size(pos,1)-1
    %%
     v = velocities(count);
     vpx = degToPix(v,60);

    dir = -directions(count); % not sure why but now right is 0, top 90, left 180, down 270
    jumpsize = 0.2 * vpx;
    [dx,dy] = pol2cart(deg2rad(180 + dir),jumpsize);
    xstart = xCenter+dx;
    ystart = yCenter+dy;
    
    [dx,dy] = pol2cart(deg2rad(dir),degToPix(15,60));
    endx = dx+ xCenter;
    endy = dy+ yCenter;
    
    
    [vx,vy] = pol2cart(deg2rad(dir),vpx);
    distance= diff([xstart,ystart;endx,endy]);
    stepsize = [vx, vy].*ifi;
    

    % get duration
    duration = random(trunc_dist)/1000; % in s
    %duration = 0;
    
    drawTarget(xCenter, yCenter,screen,20,'fixbulleye');
    LastFlip =  flip_screen(screen);
    KbStrokeWait(); 
    
    % start the trial
    drawTarget(xCenter, yCenter,screen,20,'fixbulleye');
    LastFlip =  flip_screen(screen);
    
    LastFlip = flip_screen(screen, LastFlip + duration); % image_fixcross_time = 0.5s
    sendETNotifications(eyetracking,requester,sprintf('SMOOTH PURSUIT trialstart, velocity %d, angle %d, trial %d, block %d,',velocities(count),directions(count),count ,block))
    
    % we want to start in the middle
    newPos = [xstart ystart];
    
    time0 = GetSecs;
    while ((GetSecs - time0+ifi) < (10+0.2*v)/v)
        dt = GetSecs - time0;
        pos = newPos + dt.* [vx, vy];
%         newPos = (newPos + stepsize);
        
        drawTarget(round(pos(1)),round(pos(2)),screen,1,'fixbulleye');
        
        LastFlip = flip_screen(screen, 0); % image_fixcross_time = 0.5s
        

    end
    sendETNotifications(eyetracking,requester,sprintf('SMOOTH PURSUIT trialend, velocity %d, angle %d, trial %d, block %d,',velocities(count),directions(count),count ,block))
    WaitSecs(0.5); 
    
end
sendETNotifications(eyetracking,requester,sprintf('SMOOTH PURSUIT stop, block %d', block))


