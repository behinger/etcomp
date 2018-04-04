function [last_flip] = flip_screen(scr_w,scr_h,win, time)
% calculate coordinates dependend on markersize, white frame needed?
markersize = 30;
whiteframe = ceil(0.24 * markersize); % whiteframe is the gridsize of marker (markersize / 5) * 1,2

l = markersize/2 + whiteframe;
r = scr_w - markersize/2 - whiteframe;
m =  scr_w/2;
t = markersize/2 + whiteframe;
c =   scr_h/2 ;
b = scr_h - markersize/2 -whiteframe;
rectColor = [255 255 255];
baseRect = [0 0 ceil(1.48*markersize) ceil(1.48*markersize)]; % whiteframe is the gridsize of marker (markersize / 5) * 1,2
coordinates = [l t; l c; l b; m t; m b;r t; r c; r b  ];
for  i = 1:8
    target = sprintf('surface%s',num2str(i));
    x = coordinates(i,1);
    y = coordinates(i,2);
    centeredRect = CenterRectOnPointd(baseRect, x, y);
    Screen('FillRect', win, rectColor, centeredRect);
    expDrawTarget(x,y,128,markersize,target, win);
end
[last_flip] = Screen('Flip', win, time);
