function [subject]=recallImages(const,trialinfo,visual)
%
% recall test of experiment SpatStat
%
% const       - parameters of the experiment
% el          - eyelink
% trialinfo   - trial information
% visual      - screens for visual presentation
%

tr=1; ncal=const.ncalRec;
while tr<=length(trialinfo.Rec)
    %% new trial
    clearBuffers;
    
    %% get trial info
    imgName=trialinfo.Rec(tr).Name;
    set=trialinfo.Rec(tr).Set;
    type=trialinfo.Rec(tr).Type;
    img=trialinfo.Rec(tr).Img;

    
    %% load image
    [imgDraw,coor]=loadImage(const,visual,imgName);
    dispInstructions ('InsInterTrialRec.txt',const,visual);
    
	

    %% trial

        %% prepare keyboard and mouse
        clearBuffers;
                
        %% display image
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('DrawTexture',visual.main,imgDraw,[],coor);
        Screen('Flip', visual.main);
        t1 = GetSecs;

        
        % presentation time
        [keyCode t2 Mx My Mb]=waitForResponse;
        while ~strcmp(KbName(keyCode),'esc') & ~strcmp(KbName(keyCode),const.keyCorr) & ~strcmp(KbName(keyCode),const.keyFalse)
            [keyCode t2 Mx My Mb]=waitForResponse;
        end
        
        % remove image - clear screen
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('Flip', visual.main);
        
        % response evaluation
        [corr]=responseEval(const,visual,keyCode,set);
        subject(tr).corr = corr;
        subject(tr).RT = t2-t1;
        
        
        % update variables
        Screen('Close',imgDraw);
        tr=tr+1;
        ncal=ncal+1;
    end
end