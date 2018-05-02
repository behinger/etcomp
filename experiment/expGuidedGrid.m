function []= expGuidedGrid(coords,screen,randomization, block,requester,eyetracking)
display_pos = coords(randomization,:)';
%%
targetKey    ='Space';
total_elements = size(display_pos,2);
if total_elements == 49
    condition = 'LARGEGG';
else 
    condition = 'SMALLGG';
end
lastflip = showInstruction(condition,screen,requester,eyetracking, block);

%prepare a background
%Screen('FillRect', screen.win, [screen.background_color screen.background_color screen.background_color]);
%actually show the screen with the background
%lastflip = Screen('Flip', screen.win);

sendETNotifications(eyetracking,requester,sprintf('GRID start block %d', block));

%time = 15;
%grid_buttonpress(targetKey,time,requester,eyetracking);



%walk through the positions and show the circle
for count=1:total_elements
    
    %draw the marker
    drawTarget(display_pos(1,count), display_pos(2,count),screen,20,'fixcross');
    %show the window with the current marker
    time =  flip_screen(screen, lastflip);
    sendETNotifications(eyetracking,requester,sprintf('GRID element %d posx %d posy %d total %d block %d',count,display_pos(1,count),display_pos(2,count),total_elements,block))
    
    
    grid_buttonpress(targetKey,time,requester,eyetracking);
    
    sendETNotifications(eyetracking,requester,sprintf('GRID buttonpress'))
    
    
    
end

%show extra last dot in middle of screen
drawTarget(screen.screen_width/2, screen.screen_height/2,screen,20,'fixcross');

%[time]=Screen('Flip', win);
time =  flip_screen(screen, lastflip);

sendETNotifications(eyetracking,requester,sprintf('GRID stop block %d',block))


grid_buttonpress(targetKey,time,requester,eyetracking);


%prepare a clean background
Screen('FillRect', screen.win, [screen.background_color screen.background_color screen.background_color]);
%actually show the screen with the white background
time =  flip_screen(screen, lastflip);

fprintf('\n Grid Test finished.')
end

function grid_buttonpress(targetKey,time,requester,eyetracking)
% wait for KB press and send directly afterwards a message to the ETs
waitForKB_linux(targetKey,time);
sendETNotifications(eyetracking,requester,sprintf('GRID buttonpress'))

end
