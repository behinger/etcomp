            function [] = draw_target(x,y,targetsize,which_target, win)
if strcmp(which_target, 'fixcross') == 1
%     fixCrossDimPix=targetsize/2;
%     xCoords = [-fixCrossDimPix fixCrossDimPix 0 0];
%     yCoords = [0 0 -fixCrossDimPix fixCrossDimPix];
%     lineWidthPix = 4;
%     allCoords = [xCoords; yCoords];
%     Screen('DrawLines', win, allCoords,lineWidthPix,[0 0 0], [x y]);
   
    width = 45; % horizontal dimension of display (cm)
    dist = 60; % viewing distance (cm)

    colorOval = [0 0 0]; % color of the two circles [R G B]
    colorCross = [255 255 255]; % color of the Cross [R G B] change

    d1 = 0.6; % diameter of outer circle (degrees)
    d2 = 0.2; % diameter of inner circle (degrees)
    rect = Screen('Rect',win);
    ppd = pi * (rect(3)-rect(1)) / atan(width/ dist/2) / 360; % pixel per degree

    Screen('FillOval', win, colorOval, [x-d1/2 * ppd, y-d1/2 * ppd, x+d1/2 * ppd, y+d1/2 * ppd], d1 * ppd);
    Screen('DrawLine', win, colorCross, x-d1/2 * ppd, y, x+d1/2 * ppd, y, d2 * ppd);
    Screen('DrawLine', win, colorCross, x, y-d1/2 * ppd, x, y+d1/2 * ppd, d2 * ppd);
    Screen('FillOval', win, colorOval, [x-d2/2 * ppd, y-d2/2 * ppd, x+d2/2 * ppd, y+d2/2 * ppd], d2 * ppd);


elseif contains(which_target, 'surface') == 1
    stimpath = sprintf('/net/store/nbp/users/iibs/ETComp/experiment/stimuli/%s',which_target);
    marker= imread([stimpath '.png']);
    stim = Screen('MakeTexture', win, marker);
    halfsize=targetsize/2;
    Screen('DrawTexture',win, stim, [0,0,size(marker,2),size(marker,1)],[x-halfsize,y-halfsize,x+halfsize,y+halfsize]);



       
end