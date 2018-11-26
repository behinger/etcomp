% We need matlab here because pyedfread does not give us calibration
% accuracy (or maybe it does, but I knew how to do it with edfread ;)
addpath('/net/store/nbp/projects/lib/edfread/build/linux64')
error = struct('max',[],'avg',[],'sub',[]);
for sub = 1:20
    fprintf('running subject %i \n',sub)
    subjpath = sprintf('/net/store/nbp/projects/etcomp/VP%i/raw/',sub);
    try
        d = dir([subjpath '*.EDF']);
        [~,info] = edfread(fullfile(d.folder,d.name));
        for k=1:length(info.calib)
            cal = info.calib(k);
            if isstruct(cal.right)
                c = cal.right;
                
            else
                c = cal.left;
                
            end
            error.max = [error.max c.err_max];
            error.avg = [error.avg c.err_avg];
            error.sub = [error.sub sub];
        end
        
        
    catch
        fprintf('could not read subject %i \n' ,sub)
        continue
    end
end
