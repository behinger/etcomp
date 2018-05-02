function [] = expPupilDilation(screen,randomization, eyetracking, requester, block)
showInstruction('DILATION',screen,requester,eyetracking, block);

dilation.win = screen.win;
sendETNotifications(eyetracking,requester,sprintf('DILATION start, block %d',block));

for color_id = 1:25
    dilation.background_color = randomization(color_id);

    Screen('FillRect', screen.win, [randomization(color_id) randomization(color_id) randomization(color_id)]);
    drawTarget(screen.screen_width/2, screen.screen_height/2,dilation,20,'fixbulleye');
    LastFlip = flip_screen(screen, 0);
    flip_screen(screen, LastFlip + 2.5);

    sendETNotifications(eyetracking,requester,sprintf('DILATION lum %d block %d',randomization(color_id),block))
    
end

sendETNotifications(eyetracking,requester,sprintf('DILATION stop, block %d', block));
