function trialinfo = genDesign (const)
%
% generate experimental design: SpatStat
%
% version 1.0 - 03.06.13
%

%% load images
load(const.imgFile,'NSet');

%% memorization
MemSet = repmat(1,const.repImgs*NSet(1),1);
MemImg = repmat(1:NSet(1),1,const.repImgs);
PresTime = repmat(const.PresTime,const.repImgs*NSet(1),1);
Pres=[repmat(1,NSet(1),1);repmat(2,NSet(1),1)];
order = randperm(length(MemImg));

MemSet=MemSet(order);
MemImg=MemImg(order);
PresTime=PresTime(order); 
Pres=Pres(order);
diffX=const.coor(3)-const.coor(1);
diffY=const.coor(4)-const.coor(2);

for i=1:length(MemImg)
    trialinfo.Mem(i).Name=['Set1_' num2str(MemImg(i),'%.2d')];
    trialinfo.Mem(i).Img=MemImg(i);
    trialinfo.Mem(i).Set=MemSet(i);
    load(const.imgFile,trialinfo.Mem(i).Name);
    trialinfo.Mem(i).Type=eval([trialinfo.Mem(i).Name '.type;']);
    eval(['clear ' trialinfo.Mem(i).Name]);
    trialinfo.Mem(i).PresTime=PresTime(i);
    
    if i==1
        trialinfo.Mem(i).Pres=1;
    end
   if i>1
       imaged = [trialinfo.Mem(1:i-1).Img];
       if any(imaged==trialinfo.Mem(i).Img)
    trialinfo.Mem(i).Pres=2;
    else  trialinfo.Mem(i).Pres=1;
       end
   end
end

%% recall
dummy=[];
for set=1:length(NSet)
    dummy=[dummy; repmat(set,NSet(set),1) (1:NSet(set))'];
end
order=randperm(size(dummy,1))';

RecSet = dummy(order,1);
RecImg = [1:NSet(1) 1:NSet(2)];
RecImg = RecImg(order);

for i=1:length(RecSet)
    trialinfo.Rec(i).Name=['Set' num2str(RecSet(i),'%.1d') '_' num2str(RecImg(i),'%.2d')];
    trialinfo.Rec(i).Img=RecImg(i);
    trialinfo.Rec(i).Set=RecSet(i);
    load(const.imgFile,trialinfo.Rec(i).Name);
    trialinfo.Rec(i).Type=eval([trialinfo.Rec(i).Name '.type;']);    
    eval(['clear ' trialinfo.Rec(i).Name]);
end
