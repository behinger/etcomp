function [] = expSmoothPursuit(win, screen_width, screen_height)

pos = 
for currPoint = 1:size(pos,1)-1
    time = 0;%GetSecs;
    newPos = pos(currPoint,:);
    
    distance= diff(gridPos(currPoint:(currPoint+1),:));
    stepsize = distance/(1.5*1/ifi);
    
    tic
    while ~KbCheck && ((time+ifi) < 1.5)

        newPos = newPos + stepsize;
%         newPos = [100-halfsize+gridPos,mid_y-halfsize,100+halfsize+gridPos,mid_y+halfsize]
%         stimRect = [0,0,size(marker,2),size(marker,1)];
        % TODO offset um halfsize
        
        draw_target(newPos(1),newPos(2),[],'fixcross',win)
%         Screen('DrawTexture',win, stim, stimRect,);
        lastflip  = Screen('Flip', win, lastflip + (1 - 0.5) * ifi);
         % Increment the time
        time = time + ifi;

    end
    WaitSecs(0.2)
    
end