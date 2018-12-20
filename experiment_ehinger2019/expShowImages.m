function [ ] = expShowImages(type,cfg,screen, requester, block, eyetracking, randomization)
%% Roll Head Motion
rotation_angle = [0 35 -35];
showInstruction(type,screen,requester,eyetracking, block);
sendETNotifications(eyetracking,requester,sprintf('%s start, block %d', type,block))
for count = 1:3
    
    % calculate display positions
    displayPos =[screen.screen_width/2-cfg.image_width/2,screen.screen_height/2-cfg.image_height/2,screen.screen_width/2+cfg.image_width/2,screen.screen_height/2+cfg.image_height/2];
    % for freeviewing show fix_cross before and after
    if strcmp(type,'FREEVIEW')
        %draw fix cross
        drawTarget(screen.screen_width/2, screen.screen_height/2,screen,20,'fixcross');
        LastFlip = flip_screen(screen,0);
        KbStrokeWait();
        drawTarget(screen.screen_width/2, screen.screen_height/2,screen,20,'fixcross');
        LastFlip = flip_screen(screen,0);
        
        %draw picture
        Screen('DrawTexture',screen.win,cfg.images(randomization(count)), [],[displayPos]);
        LastFlip = flip_screen(screen, LastFlip + cfg.fixcross_time + rand(1)*0.2 - 0.1); % image_fixcross_time = 0.5s
        sendETNotifications(eyetracking,requester,sprintf('FREEVIEW fixcross'))
        LastFlip = flip_screen(screen, LastFlip + cfg.image_time); % image_time = 6s
        sendETNotifications(eyetracking,requester,sprintf('FREEVIEW trial %d id %d block %d',count, randomization(count),block))
        
        %display the three pictures for the yaw condition simultaneously
        %with a fix cross
    elseif strcmp(type,'YAW')
        Screen('DrawTexture',screen.win,cfg.images(count), [],[displayPos]);
        drawTarget(screen.screen_width/2, screen.screen_height/2,screen,20,'fixcross');
        LastFlip = flip_screen(screen,0);
        LastFlip = flip_screen(screen, LastFlip + cfg.image_time);
        sendETNotifications(eyetracking,requester,sprintf('YAW trial %d block %d',count,block))

        % rotate the picture for the roll condition
    elseif strcmp(type,'ROLL')
        Screen('DrawTexture',screen.win,cfg.images, [],[displayPos],rotation_angle(count));
        drawTarget(screen.screen_width/2, screen.screen_height/2,screen,20,'fixcross');
        LastFlip = flip_screen(screen,0);
        LastFlip = flip_screen(screen, LastFlip + cfg.image_time);
        sendETNotifications(eyetracking,requester,sprintf('ROLL trial %d block %d',count,block))

    end

end
 sendETNotifications(eyetracking,requester,sprintf('%s stop, block %d', type,block))
