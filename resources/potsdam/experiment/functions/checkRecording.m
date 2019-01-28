function trialok=checkRecording(tr)
% Check recording status

error=Eyelink('CheckRecording'); 
if(error~=0)
    Eyelink('Message','TrialError %d',tr);
    trialok = 0;
else
    trialok = 1;
end