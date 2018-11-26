function [lastflip] = showInstruction(condition,screen,requester,eyetracking,block)
% display instructions
instruction = fileread([ 'Instructions/Instruction_' condition '.txt']);

Screen('FillRect', screen.win, screen.background_color);
flip_screen(screen);

% first draw instructions and wait for space
DrawFormattedText(screen.win, instruction, 'center', 'center',0, 60, [],[],[1.25]);
flip_screen(screen);
sendETNotifications(eyetracking,requester,sprintf('Instruction for %s start block %d',condition, block))


Screen('FillRect', screen.win, screen.background_color);
WaitSecs(1);

KbStrokeWait();
lastflip = flip_screen(screen);

if ~strcmp(condition, 'BEGINNING')
    %draw the red instruction target at the middle of the screen
    drawTarget(screen.screen_width/2, screen.screen_height/2,screen,20,'fixcross', screen.color_condition_begin);
    %show the first marker
    flip_screen(screen);
    KbStrokeWait();
    lastflip =  flip_screen(screen);
end
sendETNotifications(eyetracking,requester,sprintf('Instruction for %s stop block %d',condition, block));


