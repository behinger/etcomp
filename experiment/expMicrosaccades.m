function [ ] = expMicrosaccades(win, screen_width, screen_height, time, eyetracking, requester, block)

expDrawTarget(screen_width/2, screen_height/2,128,20,'fixcross', win);
LastFlip = flip_screen(screen_width,screen_height,win,time);
sendETNotifications(eyetracking,requester,sprintf('MICROSACC start block %d',block))
%pause(2) % what about screen correction time?
LastFlip = flip_screen(screen_width,screen_height,win, LastFlip);
sendETNotifications(eyetracking,requester,sprintf('MICROSACC stop block %d',block))
