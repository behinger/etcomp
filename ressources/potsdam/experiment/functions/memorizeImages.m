function [subject]=memorizeImages(const,trialinfo,visual)
%
% run trials of experiment SpatStat
%
% const       - parameters of the experiment
% el          - eyelink
% trialinfo   - trial information
% visual      - screens for visual presentation
%

tr=1; 
%time=ones(length(trialinfo.Mem),1);
%filename=sprintf('Vp_%d',const.vpnr);
%save(['Vp_' num2str(const.vpnr)],'trialinfo')


fcHor=CenterRectOnPoint(const.fcHor,const.fcx,const.fcy);
fcVer=CenterRectOnPoint(const.fcVer,const.fcx,const.fcy);
while tr<=length(trialinfo.Mem)
    %% new trial
    clearBuffers;
    
    
    
    %% get trial info
    imgName=trialinfo.Mem(tr).Name;
    set=trialinfo.Mem(tr).Set;
    type=trialinfo.Mem(tr).Type;
    img=trialinfo.Mem(tr).Img;
    PresTime=trialinfo.Mem(tr).PresTime;
    CheckTime=const.CheckTime
    cal=[const.LeftBig;const.UpBig;const.DownBig]';
    cal2=[const.LeftSmall;const.UpSmall;const.DownSmall]';
    calcol=const.calcol;
    calcol2=const.calcol2*256;
     %% load image
    [imgDraw,coor]=prepImage(const,visual,tr,imgName);
    %% Calibration
    newCal=const.ncalMem;
    
     
    
    if mod(tr,newCal)==1
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('FillOval', visual.main ,calcol ,cal);
        Screen('FillOval', visual.main ,calcol2 ,cal2);
        Screen('Flip', visual.main);
    pause()
    end
    
    
  
    %% trial

        %% prepare keyboard and mouse
        clearBuffers;
        
         %% display background black
        Screen('FillRect',visual.main,const.bgCol*256*0,[]);
        Screen('FillRect',visual.main,const.fcCol*256,fcHor);
        Screen('FillRect',visual.main,const.fcCol*256,fcVer);
        Screen('Flip', visual.main);
        
        t1 = GetSecs;


        
        % presentation time
        t2=t1;
        while t2-t1<=CheckTime
            [keyIsDown, t2, keyCode] = KbCheck;
            checkEscape(keyCode);
        end
        
        %% display background white
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        
        Screen('FillRect',visual.main,const.fcCol*0,fcHor);
        Screen('FillRect',visual.main,const.fcCol*0,fcVer);
        Screen('Flip', visual.main);
        
        t1 = GetSecs;


        
        % presentation time
        t2=t1;
        while t2-t1<=CheckTime
            [keyIsDown, t2, keyCode] = KbCheck;
            checkEscape(keyCode);
        end
        
         %% display image
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('DrawTexture',visual.main,imgDraw,[],coor);
        Screen('Flip', visual.main);
        t1 = GetSecs;
 
        
        % presentation time
        t2=t1;
        while t2-t1<=PresTime
            [keyIsDown, t2, keyCode] = KbCheck;
            checkEscape(keyCode);
        end
        
        Screen('FillRect',visual.main,const.bgCol*256*0,[]);
        Screen('Flip', visual.main);
        
        t1 = GetSecs;


        
        % presentation time
        t2=t1;
        while t2-t1<=CheckTime
            [keyIsDown, t2, keyCode] = KbCheck;
            checkEscape(keyCode);
        end
        
        
        % remove image - clear screen
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('Flip', visual.main);

        subject(tr).PresTime = t2-t1;   
        

        % update variables
        Screen('Close',imgDraw);
        
       
        
    [keyCode]=waitForResponse;
    if keyCode(67)==1
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('FillOval', visual.main ,calcol ,cal);
        Screen('FillOval', visual.main ,calcol2 ,cal2);

        Screen('Flip', visual.main);
    pause()
    end  
    
     if mod(tr,20)==0 & tr<50
        dispInstructions2('Break.txt',const,visual);
        pause()
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('FillOval', visual.main ,calcol ,cal);
        Screen('FillOval', visual.main ,calcol2 ,cal2);
        Screen('Flip', visual.main);
        
        a=0;
        while a==0
        [keyCode]=waitForResponse;
        if(keyCode(82))==1
        a=1   ;
        end
        end
        
        dispInstructions2('Break2.txt',const,visual);
        pause()
        Screen('FillRect',visual.main,const.bgCol*256,[]);
        Screen('FillOval', visual.main ,calcol ,cal);
        Screen('FillOval', visual.main ,calcol2 ,cal2);
        Screen('Flip', visual.main);
        
    end
        
        
      
tr=tr+1;
end