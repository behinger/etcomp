%% pathes
addpath('functions')

%% variables
t1=GetSecs;
const.vpnr=0;
const=allgVar(const);

%% make img file
for set=1:2
    switch set
        case 1
            nameSet='set1';
        case 2
            nameSet='set2';
    end
    n=0;
    for j=1:2
        switch j
            case 1
                imgPath=['imgs/' nameSet '/Struktur/'];
                name='Struktur';
            case 2
                imgPath=['imgs/' nameSet '/Muster/'];
                name='Muster';
        end
        imgs=dir([imgPath '*.jpg']);
        for i=1:length(imgs)
            n=n+1;

            % read image
            imgName = [imgPath imgs(i).name];
            imgData = imread(imgName);
            
            % resize image
            imgData = resizeImg(imgData,const);
            eval(['Set' num2str(set,'%.1d') '_' num2str(n,'%.2d') '.imgData= imgData;']);
            eval(['Set' num2str(set,'%.1d') '_' num2str(n,'%.2d') '.set=' num2str(set,'%.1d') ';']);
            eval(['Set' num2str(set,'%.1d') '_' num2str(n,'%.2d') '.type=' num2str(j,'%.1d') ';']);
        end
    end
    NSet(set)=n;
end
save(const.imgFile,'Set*_*','NSet');

%% remove pathes
GetSecs-t1
rmpath('functions')
