% IntoTheWild_WL_FixOnset.m


% exppath='/home/experiment/experiments/ITW/WL_FO/experiment';
% stimpath='/home/experiment/experiments/ITW/WL_FO/cutouts_';
% backgroundpath='/home/experiment/experiments/ITW/WL_FO/Background';
% resultpath='/home/experiment/experiments/ITW/WL_FO/data';

exppath='/net/store/nbp/projects/IntoTheWild/Experiment/ITW_WL_FO/experiment';
stimpath='/net/store/nbp/projects/IntoTheWild/Experiment/ITW_WL_FO/cutouts_';
backgroundpath='/net/store/nbp/projects/IntoTheWild/Experiment/ITW_WL_FO/Background';
resultpath='/net/store/nbp/projects/IntoTheWild/Experiment/ITW_WL_FO/data';


addpath(genpath(stimpath)) % stimulus path
addpath(genpath(resultpath)) %results path

%settings

expName = input('\n \n WELCOME EXPERIMENTER! \n\n What is your name? \n >','s');
subject_id = input('\n subjectid: ');

% ppdev_mex('Close', 1);

%eyetracking
eyetracking=false;
calibrate_eyelink = false;


%setup random stream
%if subject_id is used as seed for the random stream, it is possible to get
%the exact same randomization again for the same subject id
mtstream = RandStream('mt19937ar','Seed',subject_id);
if strfind(version('-release'),'2014')>0
    RandStream.setGlobalStream(mtstream)
elseif strfind(version('-release'),'2016b')>0
    RandStream.setGlobalStream(mtstream)
else
    RandStream.setDefaultStream(mtstream);
end

%setup parallel port
% ppdev_mex('Open', 1);


%parameters and setup
stimID    = 1:171;
allID     = [stimID];
stim_str  = {'f'};


% objectKey  = '1';%'KP_End'; %response to report object
% textureKey = '2';%'KP_Down'; %response to report scrambled texture


WL_FO_fixation_durMM      = [1.8 2.2]; % duration of fix dot (randomized between 1.8 and 2.2 secs)  %CHECK numbers
WL_FO_stim_dur          = 6;
% WL_FO_blankScreen_durMM = [0.2 0.4]; % approx 300ms, randomized between 200 & 400 ms
% WL_FO_blankScreen_durMM = [5.9 6.1]; % duration of fix dot (randomized between 1.8 and 2.2 secs)

WL_FO_ITI_durMM         = [1.6 2]; % inter-trial interval (blankscreen) of about 1300 ms (between 1200 and 1400 ms).


% appearance
background_color = 255;                                     %CHECK if correct!
fixPointRings = [18 10 4];
%fixPointRings = [10 6 2];
fixPointColor = [0 255 0];

% trg_colors=[100,120,150,200,225];
trg_colors=[100,150];  %on-/offset


%open screen
debug=false;
if debug
    commandwindow;
    PsychDebugWindowConfiguration;
end

whichScreen    = max(Screen('Screens'));
% ScreenSize     = get(0, 'Screensize' );
mp = get(0, 'MonitorPositions'); %using  multiple screens
ScreenSize = mp(whichScreen+1,:);
ScreenSize(2)=1;
[win, winRect] = Screen('OpenWindow',whichScreen,background_color,[0,0,ScreenSize(3),ScreenSize(4)]);

hz             = Screen('NominalFrameRate', win);
% if hz~=120
%     error('WRONG MONITOR SETTINGS. CHECK FREQUENCY!')
% end

frameCorrectionTime = 0.006; %in seconds

%setup eyetracker
if eyetracking==1
    EyelinkInit()
    el=EyelinkInitDefaults(win);% win -> PTB window
end


% initial screen filling
Screen('FillRect', win, [background_color background_color background_color]);
screen_width = winRect(3);
screen_height = winRect(4);


% fixation spot
fix_x = screen_width/2; %in px
fix_y = screen_height/2;%-30;


% trigger square
sz_sq=100;
% sq_x=winRect(3)-sz_sq;
sq_x=winRect(1);
sq_y=1951;
% sq_y=winRect(4)-sz_sq;

% sz_sq=50;
% % sq_x=winRect(3)-sz_sq;
% sq_x=winRect(1);
% sq_y=970;
% % sq_y=winRect(4)-sz_sq;


sName = input('\n Which screen are you using? \n  Asus: 1 \n  Dell: 2 \n >');

if sName==1
    screenName='Asus';
elseif sName==2
    screenName='Dell';
end


if strcmp(screenName,'Asus')
    screenWidth_mm=708.48;
elseif strcmp(screenName,'Dell')
    screenWidth_mm=552.96;
end

%px/deg-converter
pixelSize_mm       = screenWidth_mm/ScreenSize(3); %screenWidth[mm]/num pixels
viewingDistance_mm = 800;

fprintf(['\n \n SCREEN DISTANCE SHOULD BE ' num2str(viewingDistance_mm/10) 'CM! \n \n'])

mmPerDegree = tand(1)*viewingDistance_mm;
pxPerDegree = mmPerDegree ./ pixelSize_mm;

[keyboardIndices, productNames, allInfos] = GetKeyboardIndices();
keyboardIndex=keyboardIndices(strcmp(productNames,'DELL Dell USB Entry Keyboard'));

%% ----------------------- WL_FO:    Load stimuli -------------------------- %
% load all necessary information
% load(['/home/experiment/experiments/ITW/WL_FO/cutoutAnnotations_' num2str(viewingDistance_mm/10) '.mat'])


%%
load(['/net/store/nbp/projects/IntoTheWild/Experiment/ITW_WL_FO/cutoutAnnotations_' num2str(viewingDistance_mm/10) '.mat'])
%%

WLindex = nan(length(stimID),length(stim_str));

for id = 1:length(stimID)                             % ascending id
    for stim_type = 1:length(stim_str)
        
        currentIMG = imread([stimpath num2str(viewingDistance_mm/10) '/' cell2mat(coAnnotations(id).coName)]);
        
        
        % make and preload texture
        WLindex(id,stim_type)   = Screen('MakeTexture', win, currentIMG);
        [resident]              = Screen('PreloadTextures', win, WLindex(id,stim_type));
        
    end
end

%% load background
cd(backgroundpath)
dirData = dir('*.jpg');
dirData={dirData.name};

BGindex = nan(length(stimID),length(stim_str));

for id = 1:length(stimID)                             % ascending id
    for stim_type = 1:length(stim_str)
        
        bgIMG = imread([backgroundpath '/' dirData{id}]);
        
        
        % make and preload texture
        BGindex(id,stim_type)   = Screen('MakeTexture', win, bgIMG);
        [resident]              = Screen('PreloadTextures', win, BGindex(id,stim_type));
        
    end
end

cd(exppath)


%% ----------------------- WL_FO:    Randomisation ------------------------- %


blockNumber =  9;    % number of blocks
repStim     =  1;    % repetions per stimulus during the whole session

id_base  = 1:length(stimID);   % all IDs (ascending)


rnd_id = randsample(id_base,length(id_base)); %randomize order of stimuli

final_cond = rnd_id;

num_trials = size(final_cond,2);


% randomize timing
% calculate all possible times taht the fixation duration and ITI can have
% and randomize those
physicallyPossibleTimesFixdur = WL_FO_fixation_durMM(1):(1/hz):WL_FO_fixation_durMM(2); % calculate all possible times taht the fixation duration can have
WL_FO_fixation_dur = randsample(repmat(physicallyPossibleTimesFixdur,1,ceil(num_trials/length(physicallyPossibleTimesFixdur))),num_trials,false);

physicallyPossibleTimesITI = WL_FO_ITI_durMM(1):(1/hz):WL_FO_ITI_durMM(2);
WL_FO_ITI_dur = randsample(repmat(physicallyPossibleTimesITI,1,ceil(num_trials/length(physicallyPossibleTimesITI))),num_trials,false);

%% ----------------------- WL_FO:    Display ------------------------------- %

% where should stimuli be displayed?
displayPos =[ScreenSize(3)/2-size(currentIMG,2)/2,ScreenSize(4)/2-size(currentIMG,1)/2,ScreenSize(3)/2+size(currentIMG,2)/2,ScreenSize(4)/2+size(currentIMG,1)/2];

%setup time logging variables
WL_FO_trialFixationOnset  = nan(1,num_trials);
WL_FO_blankScreenOnset    = nan(1,num_trials);
WL_FO_stimOnset           = nan(1,num_trials);
WL_FO_responseOnset       = nan(1,num_trials);
WL_FO_trialEnd            = nan(1,num_trials);

WL_FO_trialFixationOnsetVBL  = nan(1,num_trials);
WL_FO_blankScreenOnsetVBL    = nan(1,num_trials);
WL_FO_stimOnsetVBL           = nan(1,num_trials);
WL_FO_responseOnsetVBL       = nan(1,num_trials);

WL_FO_blockStart          = [];
WL_FO_blockEnd            = [];
WL_FO_trialBlock          = nan(1,num_trials);
WL_FO_subjectID           = nan(1,num_trials);



%start and setup time
fprintf('WL_FO: Ready to go.\n')
EEGtimestamp = datestr(now,'yyyymmdd_HHMM');
EEG_started = input(sprintf('Has the EEG file been started? (filename: ITW_WLFO_subj%u) \n (1) - Confirm. \n >',subject_id));
while EEG_started ~= 1
    EEG_started = input(sprintf('Has the EEG file been started? (filename: ITW_WLFO_subj%u) \n (1) - Confirm. \n >',subject_id));
end


start_task = input('(1) - Start WL_FO.\n >');
while start_task ~= 1
    start_task = input('(1) - Start WL_FO.\n >');
end

WL_FO_start = datestr(now);
HideCursor;

draw_instructions_and_wait(['Welcome to the lab. \n\n', ...
    'In the following, each stimulus presented will show a natural scene. \n\n'...
    'You are allowed to freely explore the scene. \n Before each scene, you will see a fixation dot. Please remain fixated until it disappears. \n\n' ...
    'At the beginning of the experiment and after each third block, we will calibrate the eytracker. \n\n' ...
    'At the end of each block we will do a self-paced eyetracker validation. \n' ...
    'You will see a target that you have to fixate on.' ...
    'Once you fixate in it press the space bar to lock the position. Then the next target will appear. \n\n' ...
    'After each block you can take a break for as long as you want to. \n\n'...
    'This phase will take about 35 minutes to complete. \n\n' ...
    'Please let us know if there are any open questions. Otherwise press SPACE to start.'],background_color,win,1) % In Rossions experiment the tip of the nose for faces, or mid-distance between the head lights of the cars were at the centre of the screen

Screen('FillRect', win, [background_color background_color background_color]);

%%
% calibrationPupilLabs(screen_width,screen_height,win,ScreenSize);
%%

%setup eyelink
if eyetracking==1
    setup_eyetracker;
    %open log file
    Eyelink('OpenFile', sprintf('WLFO_s%u.EDF',subject_id));          %CHANGE file name ?
    sessionInfo = sprintf('%s %s','SUBJECTINDEX',num2str(subject_id));
    Eyelink('message','METAEX %s',sessionInfo);
    
    %send first triggers
    send_trigger(0,eyetracking);
    send_trigger(200,eyetracking);
    
    
    %start calibration
    if calibrate_eyelink
        fprintf('\n\nEYETRACKING CALIBRATION...')
        EyelinkDoTrackerSetup(el);
        fprintf('DONE\n\n')
    end
end

%setup keyboard
KbQueueRelease()
keyList                                          = zeros(1,256);
% keyList([KbName(objectKey), KbName(textureKey)]) = 1;
% KbQueueCreate(keyboardIndex,keyList)

%%
trials_per_block = num_trials/blockNumber;
block_count = num_trials/blockNumber:num_trials/blockNumber:num_trials-num_trials/blockNumber;
trial = 0; %initialize over-blocks trial counter


for block = 1:blockNumber
    
    
    
    if eyetracking==1  %recalibrate after block 3 and 6
        if block>1 && mod(block,3)==1
            if calibrate_eyelink
                fprintf('\n\nEYETRACKING CALIBRATION...')
                EyelinkDoTrackerSetup(el);
                fprintf('DONE\n\n')
            end
        end
    end
    
    WL_FO_blockStart = [WL_FO_blockStart GetSecs];
    
    
    for trial_i = 1:block_count(1)  %length(stimID)*repStim
        
        trial = trial + 1;
        trial_num = (block-1)*trials_per_block+trial_i;
        stim_index=final_cond(trial_num);
        
        fprintf('Block # %u --- Trial # %u \n',block,trial_i)
        
        
        %fixation screen pre stimulus
        ShowFixationCircles(win,winRect,fixPointRings,fixPointColor,fix_x,fix_y);
        [WL_FO_trialFixationOnsetVBL(trial), LastFlip] = Screen('Flip', win);
        WL_FO_trialFixationOnset(trial) = LastFlip;

        if eyetracking==1 && calibrate_eyelink
            Eyelink('message','SYNCTIME'); %this is t=0 for any data following
        end
        
        
        %         %blank screen pre stimulus
        %         [WL_FO_blankScreenOnsetVBL(trial), LastFlip] = Screen('Flip', win, LastFlip+WL_FO_fixation_dur-frameCorrectionTime);
        %         WL_FO_blankScreenOnset(trial) = LastFlip;
        
        
        %stimulus onset
        if eyetracking==1 && calibrate_eyelink
            Eyelink('message','TRIALID %d', trial);
            trialInfo = sprintf('%s %s','trial',num2str(trial));
            Eyelink('message','METATR %s', trialInfo);
            trialInfo = sprintf('%s %s','pic_num',num2str(stim_index));
            
            Eyelink('message','METATR %s', trialInfo);
            Eyelink('StartRecording');
            Eyelink('WaitForModeReady', 100);
        end
        
        % draw texture and fit it to full screen size.
        % ATTENTION! PTB starts counting at 0!!!!
        Screen('DrawTexture',win, BGindex(stim_index), [0,0,size(bgIMG,2),size(bgIMG,1)],[0,0,ScreenSize(3),ScreenSize(4)]);
        Screen('DrawTexture',win, WLindex(stim_index), [0,0,size(currentIMG,2),size(currentIMG,1)],displayPos);
        Screen('FillRect', win, trg_colors(1), [sq_x, sq_y,  sq_x+sz_sq,  sq_y+sz_sq] );
        
        [WL_FO_stimOnsetVBL(trial), LastFlip] = Screen('Flip', win, LastFlip+WL_FO_fixation_dur(trial)-frameCorrectionTime);

        %lptwrite(1, stim_index); % category ID as onset-trigger
        
        if eyetracking % send onset trigger
            send_trigger(stim_index,eyetracking);
        end
        
        
        %stimulus offset
        [WL_FO_responseOnsetVBL(trial), LastFlip] = Screen('Flip', win, LastFlip+WL_FO_stim_dur-frameCorrectionTime);                    % CHECK what R. displayed for response request
        %         %lptwrite(1, cat_ids(block,trial_i)+10); % % category ID+10 as offset-trigger
        WL_FO_responseOnset(trial) = LastFlip;
        
        
        if eyetracking  % send offset trigger
            send_trigger(180,eyetracking);
        end
        
        %stop ET recording after offset trigger
        if eyetracking==1 && calibrate_eyelink
            Eyelink('StopRecording');
        end
        
        %         Screen('FillRect', win, trg_colors(2), [sq_x, sq_y,  sq_x+sz_sq,  sq_y+sz_sq] );
        %         [WL_FO_stimOnsetVBL(trial), LastFlip] = Screen('Flip', win, LastFlip+WL_FO_blankScreen_dur(trial)-frameCorrectionTime);
        
        [WL_FO_trialEnd(trial), LastFlip] = Screen('Flip', win, LastFlip+WL_FO_ITI_dur(trial)-frameCorrectionTime);                    % CHECK what R. displayed for response request
        
        %         cnt=0;
        %         while GetSecs < LastFlip+WL_FO_ITI_dur(trial) %wait until ITI is over
        %             while GetSecs > LastFlip+0.5 && cnt==0
        %                 Screen('Flip', win, LastFlip+WL_FO_ITI_dur-frameCorrectionTime);
        %                 cnt=1;
        %
        %             end
        %
        %
        %             %             for flips=1:cat_ids(block,trial_i)
        %             %                 Screen('FillRect', win, trg_colors(2), [sq_x, sq_y,  sq_x+sz_sq,  sq_y+sz_sq] )
        %             %                 [WL_FO_stimOnsetVBL(trial), LastFlip] = Screen('Flip', win, LastFlip+WL_FO_blankScreen_dur(trial)-frameCorrectionTime+0.01);
        %             %                 [WL_FO_stimOnsetVBL(trial), LastFlip] = Screen('Flip', win, LastFlip+WL_FO_blankScreen_dur(trial)-frameCorrectionTime+0.01);
        %             %             end
        %
        %         end
        
        %         WL_FO_trialEnd(trial) = GetSecs;
        WL_FO_trialBlock(trial) = block;
        
        %         if eyetracking==1 && calibrate_eyelink
        %             Eyelink('StopRecording');
        %         end
        
    end
    
    WL_FO_blockEnd = [WL_FO_blockEnd GetSecs];
    
    % do custom validation at the end of the block
    if eyetracking
        Eyelink('message','BLOCKID %d', block);
        Eyelink('message','CUSTOMID %d', block-1);
        Eyelink('StartRecording');
        Eyelink('WaitForModeReady', 100);
        
        if eyetracking  % send button press trigger
            send_trigger(212,eyetracking)
        end
        
        customCalibTest(screen_width,screen_height,win,ScreenSize,subject_id,block);
        
        if eyetracking  % send button press trigger
            send_trigger(214,eyetracking)
        end
        
        Eyelink('StopRecording');
    end
    
    
    %request permission to proceed
    if block ~= blockNumber
        to_the_block = input(['Confirm: \n (1) - Start block ', num2str(block+1), '\n > ']);
        while to_the_block ~= 1
            to_the_block = input(['Confirm: \n (1) - Start block ', num2str(block+1), '\n > ']);
        end
    end
    
end



if eyetracking  % send experiment end trigger
    send_trigger(255,eyetracking)
end


ShowCursor;
KbQueueRelease(keyboardIndex)
Screen('Close') %cleans up all textures
DrawFormattedText(win, 'The experiment is complete! Thank you very much for your participation!', 'center', 'center',0, 60);
Screen('Flip', win)


%% ------------- WL_FO Data saving -----------------------------------------

delphi.subjectID                 = subject_id.* ones(1,num_trials);
delphi.experiment                = 'ITW_WL_FO';
delphi.experimenter              = expName;

delphi.win                       = winRect;
delphi.screenName                = screenName;
delphi.screenFrq                 = hz;
delphi.px_mm_hardcode            = pixelSize_mm;
delphi.px_degree_convert         = pxPerDegree;
delphi.viewDistance_mm           = viewingDistance_mm;
delphi.magnificationFactor       = [coAnnotations.magnificationFactor];

delphi.background                = background_color;
delphi.fixcolor                  = fixPointColor;
delphi.fixrings                  = fixPointRings;
delphi.fixation                  = [fix_x,fix_y];

delphi.IDFC_eyetracking          = eyetracking;

delphi.WL_FO_picID               = final_cond;
delphi.coArea                    = [coAnnotations(final_cond).coArea];
delphi.numFaces                  = [coAnnotations(final_cond).numFaces];
delphi.coFaces                   = [coAnnotations(final_cond).coFaces];
delphi.human                     = [coAnnotations(final_cond).human];
delphi.coDeecisionBase           = [coAnnotations(final_cond).coDecision];
delpi.origPic                    = [coAnnotations(final_cond).filename];

delphi.WL_FO_blockStart          = WL_FO_blockStart;
delphi.WL_FO_blockEnd            = WL_FO_blockEnd;

delphi.WL_FO_trialOnset          = WL_FO_trialFixationOnset;
delphi.WL_FO_blankScreenOnset    = WL_FO_blankScreenOnset;
delphi.WL_FO_stimOnset           = WL_FO_stimOnset;
delphi.WL_FO_responseOnset       = WL_FO_responseOnset;
delphi.WL_FO_trialOnsetVBL       = WL_FO_trialFixationOnsetVBL;
delphi.WL_FO_blankScreenOnsetVBL = WL_FO_blankScreenOnsetVBL;
delphi.WL_FO_stimOnsetVBL        = WL_FO_stimOnsetVBL;
delphi.WL_FO_responseOnsetVBL    = WL_FO_responseOnsetVBL;
delphi.WL_FO_trialEnd            = WL_FO_trialEnd;




outputname = [resultpath sprintf('/WLFO_subj%u',subject_id)];
%
%
% scriptname = [outputname '.m'];
% scriptpath = [mfilename('fullpath') '.m'];
% scriptdest = ['results/scriptbackup_subject' num2str(subject_id) '_' scriptname];


% outputname = [outputname '_' datestr(now,'yyyymmdd_HHMMSS')];
% scriptdest = [scriptdest '_' datestr(now,'yyyymmdd_HHMMSS')];
fullmatfile = sprintf('%s.mat',outputname);


if eyetracking==1 && calibrate_eyelink
    fulledffile = sprintf('%s.EDF',outputname);
    Eyelink('CloseFile');
    Eyelink('WaitForModeReady', 500);
    Eyelink('ReceiveFile',sprintf('WLFO_s%u.EDF',subject_id),fulledffile);
    Eyelink('WaitForModeReady', 500);
end

save(fullmatfile);
%copyfile(scriptpath,scriptdest);

fprintf('WL_FO done.\n')

EEG_stopped = input(sprintf('Has the EEG file been closed? (filename: ITW_WLFO_subj%u) \n (1) - Confirm. \n >',subject_id));
while EEG_stopped ~= 1
    EEG_stopped = input(sprintf('Has the EEG file been closed? (filename: ITW_WLFO_subj%u) \n (1) - Confirm. \n >',subject_id));
end


