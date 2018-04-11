function rect=EyelinkDrawCalTarget(el, x, y)

% draw simple calibration target
%
% USAGE: rect=EyelinkDrawCalTarget(el, x, y)
%
%		el: eyelink default values
%		x,y: position at which it should be drawn
%		rect: 

% simple, standard eyelink version
%   22-06-06    fwc OSX-ed

fprintf('here %f, %f\n',x,y)

rect = @(size)CenterRectOnPoint([0,0,size size],x,y);
Screen('FillOval', el.window,0  ,rect(60))
Screen('FillOval', el.window,255,rect(38))
Screen('FillOval', el.window,0  ,rect(19))
Screen('FillOval', el.window,255,rect(3))
% Screen('Flip',el.window)
flip_screen(el.screen)

rect =rect(60);

