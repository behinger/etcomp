function [corr]=responseEval(const,visual,keyCode,set)
% response evaluation

corr=0;
if (set==1 & strcmp(KbName(keyCode),const.keyCorr)) | (set==2 & strcmp(KbName(keyCode),const.keyFalse))
    corr=1;
else
    sound(const.beepRT);
    Screen('FillRect',visual.main,[255 0 0],visual.rect);
    Screen('DrawText',visual.main,'Falsche Antwort!!!',100,100,[0 0 0]);
    Screen('DrawText',visual.main,'Weiter mit Pfeiltasten.',100,924,[0 0 0]);
    Screen('Flip',visual.main);
    waitForResponse;
end