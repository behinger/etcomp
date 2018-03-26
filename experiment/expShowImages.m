function [ ] = expShowImages(type,cfg,screen_width,screen_height, win, requester, block, eyetracking)
%% Roll Head Motion
rotation_angle = [0 45 -45];

for count = 1:3
    
    % calculate display positions
    displayPos =[screen_width/2-cfg.image_width/2,screen_height/2-cfg.image_height/2,screen_width/2+cfg.image_width/2,screen_height/2+cfg.image_height/2];
    % for freeviewing show fix_cross before and after
    if strcmp(type,'freeviewing')
        %draw fix cross
        expDrawTarget(screen_width/2, screen_height/2,20,'fixcross', win);
        LastFlip = flip_screen(screen_width,screen_height,win,0);
        
        %draw picture
        Screen('DrawTexture',win,cfg.images(cfg.randomization(count)), [0,0,cfg.image_width,cfg.image_height],[displayPos]);
        LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + cfg.fixcross_time + rand(1)*0.2 - 0.1); % image_fixcross_time = 0.5s
        sendETNotifications(eyetracking,requester,sprintf('FREEVIEW fixcross'))
        LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + cfg.image_time); % image_time = 6s
        sendETNotifications(eyetracking,requester,sprintf('FREEVIEW trial %d id %d block %d',count,cfg.randomization(count),block))
        
        %display the three pictures for the yaw condition simultaneously
        %with a fix cross
    elseif strcmp(type,'yaw')
        Screen('DrawTexture',win,cfg.images(count), [0,0,cfg.image_width,cfg.image_height],[displayPos]);
        expDrawTarget(screen_width/2, screen_height/2,20,'fixcross', win);
        LastFlip = flip_screen(screen_width,screen_height,win,0);
        LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + cfg.image_time);
        sendETNotifications(eyetracking,requester,sprintf('Yaw trial %d block %d',count,block))

        % rotate the picture for the roll condition
    elseif strcmp(type,'roll')
        Screen('DrawTexture',win,cfg.images, [0,0,cfg.image_width,cfg.image_height],[displayPos],rotation_angle(count));
        expDrawTarget(screen_width/2, screen_height/2,20,'fixcross', win);
        LastFlip = flip_screen(screen_width,screen_height,win,0);
        LastFlip = flip_screen(screen_width,screen_height,win, LastFlip + cfg.image_time);
        sendETNotifications(eyetracking,requester,sprintf('Roll trial %d block %d',count,block))

    end

end