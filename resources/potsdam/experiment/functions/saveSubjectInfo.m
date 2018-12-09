function saveSubjectInfo(trialinfo,const,subject)
% save subject information

nameOut=['data/' const.code '.mat'];
if exist(nameOut,'file')
    name=dir(['data/' const.code '.mat']);
    nameOut2=['data/' const.code '_' date '.mat'];
    copyfile(nameOut,nameOut2);
end
save(nameOut,'const','trialinfo','subject');
