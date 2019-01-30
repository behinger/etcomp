function [] = expRotation(first,screen, eyetracking, requester, rand,block)
% YAW and ROLL conditions
if strcmp(first,'SHAKE')
    order = {'SHAKE','TILT'};
else
    order = {'TILT','SHAKE'};
end

% We cross balanced the order
for k = order
    
    if strcmp(k{1},'SHAKE')
        showInstruction('SHAKE',screen,requester,eyetracking, block);
        rotate(screen, eyetracking, requester, rand.shake, block);
    elseif strcmp(k{1},'TILT')
        showInstruction('TILT',screen,requester,eyetracking, block);
        tilt(screen, eyetracking, requester, rand.tilt, block);
    else
        error('unknown condition')
        
    end
end





    function [] = rotate(screen, eyetracking, requester, rand, block)
        centerX = screen.screen_width/2;
        centerY = screen.screen_height/2;
        % define 5 coordinates for the points
        %         dist = centerX/3;
        %         l = dist;
        %         lm = dist*2;
        %         rm = screen.screen_width -2*dist;
        %         r = screen.screen_width -dist;
        %         coordX = [l lm rm r];
        %         coordX = [coordX coordX];
        %         coordX = coordX(randperm(length(coordX)));
        coordX = centerX + centerX.*rand;
        sendETNotifications(eyetracking,requester,sprintf('SHAKE start block %d',block))
        
        for count =1 : length(coordX)
            %             drawTarget(centerX,centerY,screen,20,'fixcross');
            %             flip_screen(screen,2);
            %             sendETNotifications(eyetracking,requester,sprintf('SHAKE block %d center',block))
            
            %             KbStrokeWait();
            %
            
            drawTarget(coordX(count),centerY,screen,20,'fixcross');
            flip_screen(screen,2);
            sendETNotifications(eyetracking,requester,sprintf('SHAKE block %d x %d, y %d',block, coordX(count),centerY));
            %
            KbStrokeWait();
            
            
        end
        sendETNotifications(eyetracking,requester,sprintf('SHAKE stop block %d',block))
        
    end


    function [] = tilt(screen, eyetracking, requester, angles, block)
        centerX = screen.screen_width/2;
        centerY = screen.screen_height/2;
        % smooth the line
        Screen('BlendFunction', screen.win, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        
        % all angles we want to capure (0 is a horizontal line)
        %         angles = [5 -5 10 -10 15 -15];
        %         angles = [angles angles];
        
        %         angles = angles(randperm(length(angles)));
        lineLength = 400; % length of the line
        sendETNotifications(eyetracking,requester,sprintf('TILT start block %d',block))
        
        for count=1: length(angles)
            angle = angles(count);
            % calculate coordinates
            [xEnd,yEnd] = pol2cart(deg2rad(180 + angle),lineLength);
            xyCoords = [ -xEnd  xEnd; -yEnd yEnd];
            Screen('DrawLines', screen.win, xyCoords, 4, [0 0 0],[centerX centerY],1);  % change 1 to 0 to draw non anti-aliased lines.
            
            drawTarget(centerX,centerY,screen,20,'fixcross'); % draw another fix cross in the middle
            
            flip_screen(screen,2);
            sendETNotifications(eyetracking,requester,sprintf('TILT angle %d block %d ',angle,block))
            KbStrokeWait();
        end
        sendETNotifications(eyetracking,requester,sprintf('TILT stop block %d',block))
        
    end


end
