function [] = drawTarget(x,y,screen,targetsize,which_target,fix_color)
if strcmp(which_target, 'fixcross') == 1
    if isempty(screen.background_color)
        screen.background_color = 128;
    end
    
    width = 45; % horizontal dimension of display (cm)
    dist = 60; % viescreen.wing distance (cm)
    
    if nargin == 5
        colorOval = [255 255 255];
    else
        colorOval = fix_color;
    end
    % color of the two circles [R G B]
    colorCross = [screen.background_color screen.background_color screen.background_color]; % color of the Cross [R G B] change
    
    d1 = 0.6; % diameter of outer circle (degrees) (0.6)
    d2 = 0.2; % diameter of inner circle (degrees)
    rect = Screen('Rect',screen.win);
    ppd = pi * (rect(3)-rect(1)) / atan(width/ dist/2) / 360; % pixel per degree
    
    Screen('FillOval', screen.win, colorOval, [x-d1/2 * ppd, y-d1/2 * ppd, x+d1/2 * ppd, y+d1/2 * ppd], d1 * ppd);
    Screen('DrawLine', screen.win, colorCross, x-d1/2 * ppd, y, x+d1/2 * ppd, y, d2 * ppd);
    Screen('DrawLine', screen.win, colorCross, x, y-d1/2 * ppd, x, y+d1/2 * ppd, d2 * ppd);
    Screen('FillOval', screen.win, colorOval, [x-d2/2 * ppd, y-d2/2 * ppd, x+d2/2 * ppd, y+d2/2 * ppd], d2 * ppd);
    
    
elseif contains(which_target, 'fixbulleye') == 1
    
    targetVisAngle = 0.5;
    px_per_deg = 1/0.026355;
    %Set black/white & gray
    white = WhiteIndex(0);
    black = BlackIndex(0);
    colorFac = white/2;
    background = 1*colorFac;
    
    %Circle & Line parameters
    
    radL = round(0.5*targetVisAngle * px_per_deg); % diameter of outer circle
    diamL = 2*radL+1;
    radS = round(0.5*0.2 * px_per_deg); %Inner circle with diameter of 0.2°
    
    %Circles
    circleRect = ones(diamL, diamL)*screen.background_color; %Rectangle to plot circles in
    
    destRect = [0 0 (diamL) (diamL)];
    rect = Screen('Rect',screen.win);
    
    [destRect, ~, ~] = CenterRect(destRect, rect);
    
    %Define which fields are lying within the circle and make circle texture
    X = repmat((1:diamL), diamL, 1);
    Y = repmat((1:diamL)', 1, diamL);
    ctr_XY = (diamL+1)/2;
    
    circleRect(sqrt((X-ctr_XY).^2 + (Y-ctr_XY).^2) <= radL) = black;
    circleRect(sqrt((X-ctr_XY).^2 + (Y-ctr_XY).^2) <= radS) = white;
    TexCircle = Screen('MakeTexture', screen.win, circleRect);
    
    
    %Draw Bulleye
    Screen('drawTexture', screen.win, TexCircle, [], destRect);
    
end