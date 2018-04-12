function rect=local_EyelinkDrawCalTarget(el, x, y)

% draw simple calibration target
%
% USAGE: rect=EyelinkDrawCalTarget(el, x, y)
%
%		el: eyelink default values
%		x,y: position at which it should be drawn
%		rect: 

% simple, standard eyelink version
%   22-06-06    fwc OSX-ed

% fprintf('here %f, %f\n',x,y)

% %%
rect = @(size)CenterRectOnPoint([0,0,0.5*size 0.5*size],x,y);

% This is the calibration target
Screen('FillOval', el.window,0  ,rect(190));
Screen('FillOval', el.window,255,rect(120));
Screen('FillOval', el.window,0  ,rect(60));
% Screen('FillOval', el.window,255,rect(44))


% This is the STOP target
% Screen('FillOval', el.window,0  ,rect(220))
% Screen('FillOval', el.window,255,rect(140))
% Screen('FillOval', el.window,0  ,rect(90))
% Screen('FillOval', el.window,255,rect(44))


%  Screen('Flip',el.window)
% %%
flip_screen(el.screen);

rect =rect(60);

