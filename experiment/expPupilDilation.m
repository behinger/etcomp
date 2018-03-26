function [] = expPupilDilation(win,screen_width,screen_height,randomization, eyetracking, requester, block)
for color_id = 1:25
    Screen('FillRect', win, [randomization(color_id) randomization(color_id) randomization(color_id)]);
    expDrawTarget(screen_width/2, screen_height/2,20,'fixcross', win);
    LastFlip = flip_screen(screen_width,screen_height,win, 0);
    flip_screen(screen_width,screen_height,win, LastFlip + 2);

    sendETNotifications(eyetracking,requester,sprintf('DILATION lum %d block %d',color_id,block))
    
end