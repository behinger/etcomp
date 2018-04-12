function erasecaltarget(el, rect)

% erase calibration target
%
% USAGE: erasecaltarget(el, rect)
%
%		el: eyelink default values
%		rect: rect that will be filled with background colour 
if ~IsEmptyRect(rect)
    Screen( 'FillOval', el.window, el.backgroundcolour,  rect );
    flip_screen(el.screen);
end
