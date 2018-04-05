function [last_flip] = flip_screen(scr_w,scr_h,win, time)

% calculate coordinates dependend on markersize, white frame needed?
markersize = 60;
whiteframe = ceil(0.24 * markersize); % whiteframe is the gridsize of marker (markersize / 5) * 1,2
if nargin == 3
    time = 0;
end
l = markersize/2 + whiteframe;
r = scr_w - markersize/2 - whiteframe;
m =  scr_w/2;
t = markersize/2 + whiteframe;
c =   scr_h/2 ;
b = scr_h - markersize/2 -whiteframe;
lm = m/2;
rm = r - m/2;
tm = c/2;
bm = b- c/2;

rectColor = [255 255 255];
baseRect = [0 0 ceil(1.48*markersize) ceil(1.48*markersize)]; % whiteframe is the gridsize of marker (markersize / 5) * 1,2
coordinates = [l t; l tm; l c; l bm; l b; lm t; m t; rm t; lm b;m b;rm b;r t; r tm; r c; r bm; r b  ];

for  i = 1:16
    target = sprintf('surface%s',num2str(i));
    x = coordinates(i,1);
    y = coordinates(i,2);
    centeredRect = CenterRectOnPointd(baseRect, x, y);
    Screen('FillRect', win, rectColor, centeredRect);
    expDrawTarget(x,y,128,markersize,target, win);
end
[last_flip] = Screen('Flip', win, time);
