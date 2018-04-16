function [last_flip] = flip_screen(screen, time)

% calculate coordinates dependend on markersize, white frame needed?
markersize = screen.surface_marker_size;
whiteframe = ceil(0.24 * markersize); % whiteframe is the gridsize of marker (markersize / 5) * 1,2
if nargin == 1
    time = 0;
end
l = markersize/2 + whiteframe;
r = floor(screen.screen_width - markersize/2 - whiteframe);
m =  screen.screen_width/2;
t = floor(markersize/2 + whiteframe);
c =   screen.screen_height/2 ;
b = ceil(screen.screen_height - markersize/2 -whiteframe);
lm = (m-l)/2 + l;
rm = screen.screen_width - lm;
tm = (c-t)/2 + t;
bm = screen.screen_height- tm;

rectColor = [255 255 255];
baseRect = [0 0 ceil(1.48*markersize) ceil(1.48*markersize)]; % whiteframe is the gridsize of marker (markersize / 5) * 1,2
coordinates = [l t; l tm; l c; l bm; l b; lm t; m t; rm t; lm b;m b;rm b;r t; r tm; r c; r bm; r b  ];

for  count = 1:length(screen.surface_marker)

    %target = sprintf('surface%s',num2str(i));
    x = coordinates(count,1);
    y = coordinates(count,2);
    marker = screen.surface_marker(count);
    centeredRect = CenterRectOnPointd(baseRect, x, y);
    Screen('FillRect', screen.win, rectColor, centeredRect);
    Screen('DrawTexture',screen.win, screen.surface_marker(count),[],[x-markersize/2,y-markersize/2,x+markersize/2,y+markersize/2]);
end
[last_flip] = Screen('Flip', screen.win, time);
