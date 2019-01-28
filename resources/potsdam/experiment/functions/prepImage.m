function [imgDraw,coor]=prepImage(const,visual,tr,imgName)
% load image

% minimum pause duration
t1=GetSecs;

% info screen
Screen('FillRect',visual.main,const.bgCol*256,[]);
Screen('DrawText',visual.main,'Lade Bild',100,100);
Screen('Flip', visual.main);



% load image
[imgDraw,coor]=loadImage(const,visual,imgName);

% minimum pause duration between trials
t2=GetSecs;
while t2<t1+const.MinDurPause
    t2=GetSecs;
end

% continue after button press
dispInstructions ('InsInterTrialMem.txt',const,visual);