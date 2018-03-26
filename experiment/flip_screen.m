function [last_flip] = flip_screen(scr_w,scr_h,win, time)
% calculate coordinates dependend on markersize, white frame needed?
whiteframe = 5;
markersize = 40;
l = markersize/2 + whiteframe;
r = scr_w - markersize/2 - whiteframe;
m =  scr_w/2;
t = markersize/2 + whiteframe;
c =   scr_h/2 ;
b = scr_h - markersize/2 -whiteframe;
coordinates = [l t; l c; l b; m t; m b;r t; r c; r b  ];
for  i = 1:8
    target = sprintf('surface%s',num2str(i));
    x = coordinates(i,1);
    y = coordinates(i,2);
    expDrawTarget(x,y,markersize,target, win);
end
[last_flip] = Screen('Flip', win, time);
