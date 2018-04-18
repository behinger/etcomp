function [] = expRotation(type,screen, eyetracking, requester, block)
% YAW and ROLL conditions
centerX = screen.screen_width/2;
centerY = screen.screen_height/2;

if strcmp(type, 'YAW')
   
   drawTarget(centerX,centerY,screen,20,'fixcross');
   flip_screen(screen,2);
   
    
else
    
    
end

