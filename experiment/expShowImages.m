function [ ] = expShowImages(type,images,image_width,image_height win)

%% Roll Head Motion

rotation_angle = [0 45 -45];
for count = 1:3
    
    displayPos =[cfg.screen_width/2-cfg.image_yaw_width/2,cfg.screen_height/2-cfg.image_yaw_height/2,cfg.screen_width/2+cfg.image_yaw_width/2,cfg.screen_height/2+cfg.image_yaw_height/2];
    if strcmp(type,'roll')
        Screen('DrawTexture',cfg.win,cfg.images, [0,0,cfg.image_yaw_width,cfg.image_yaw_height],[displayPos],rotation_angle(count));
        draw_target(cfg.screen_width/2, cfg.screen_height/2,20,'fixcross', cfg.win);      
    end
    
    LastFlip = flip_screen(cfg.screen_width,cfg.screen_height,cfg.win,0);
    
    LastFlip = flip_screen(cfg.screen_width,cfg.screen_height,cfg.win, LastFlip + cfg.image_time_faces); % cfg.image_fixcross_time = 0.5s
    %sendETNotifications(eyetracking,requester,sprintf('FREEVIEW fixcross'))
    
    %sendETNotifications(eyetracking,requester,sprintf('FREEVIEW trial %d id %d block %d',count,rand_block.freeviewing(count),block))
    
    %   pause(2)
    % show stimulus for certain time
end