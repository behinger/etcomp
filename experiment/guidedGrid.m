function []= guidedGrid(coords,screen_width,screen_height,win,randomization, block,requester,eyetracking)
display_pos = coords(randomization,:)';


%%
targetKey    ='Space';
background_color = 128;

%prepare a background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the background
lastflip = Screen('Flip', win);


%draw the first dot at the middle of the screen
draw_target(screen_width/2, screen_height/2,20,'fixcross', win);
%show the first marker
time =  flip_screen(screen_width,screen_height,win, lastflip);

sendETNotifications(eyetracking,requester,sprintf('GRID start'))

grid_buttonpress(targetKey,time,requester,eyetracking);



%walk through the positions and show the circle
total_elements = size(display_pos,2);
for count=1:total_elements
    
    %draw the marker
    draw_target(display_pos(1,count), display_pos(2,count),20,'fixcross', win);
    %show the window with the current marker
    time =  flip_screen(screen_width,screen_height,win, lastflip);
    sendETNotifications(eyetracking,requester,sprintf('GRID element %d posx %d posy %d total %d block %d',count,display_pos(1,count),display_pos(2,count),total_elements,block))

    
    grid_buttonpress(targetKey,time,requester,eyetracking);
    
    sendETNotifications(eyetracking,requester,sprintf('GRID buttonpress'))
    
    
    
end

%show extra last dot in middle of screen
draw_target(screen_width/2, screen_height/2,20,'fixcross', win);

%[time]=Screen('Flip', win);
time =  flip_screen(screen_width,screen_height,win, lastflip);

sendETNotifications(eyetracking,requester,sprintf('GRID stop'))


grid_buttonpress(targetKey,time,requester,eyetracking);


%prepare a clean background
Screen('FillRect', win, [background_color background_color background_color]);
%actually show the screen with the white background
time =  flip_screen(screen_width,screen_height,win, lastflip);

fprintf('\n Grid Test finished.')
end

function grid_buttonpress(targetKey,time,requester,eyetracking)
% wait for KB press and send directly afterwards a message to the ETs
waitForKB_linux(targetKey,time);
sendETNotifications(eyetracking,requester,sprintf('GRID buttonpress'))

end