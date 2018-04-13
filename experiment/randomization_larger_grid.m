function [ix_out] = randomization_larger_grid()

[xx,yy] = meshgrid(linspace(-10,10,7),linspace(-7,7,7));
xx = xx(:);
yy = yy(:);
entr= @(x)-sum(x(x~=0).*log2(x(x~=0)));

centers = 1:17;
d = diff(centers)/2;
edges = [centers(1)-d(1), centers(1:end-1)+d, centers(end)+d(end)];

centers = linspace(-pi,pi,10);
centers = centers(1:end-1);
d = diff(centers)/2;
edgesangle = [centers(1)-d(1), centers(1:end-1)+d, centers(end)+d(end)];


bestent = 0;
k = 0;
%%
while true
    k = k+1;
    ix = randperm(49);
    ix(ix==25) = [];
    xx2 = xx([25 ix]);
    yy2 = yy([25 ix]);
    
    di = sqrt(diff(xx2).^2 + diff(yy2).^2);
    diang = atan2(diff(xx2),diff(yy2));
    tang = histc(diang,edgesangle);
    t    = histc(di,edges);

    t    = t./sum(t);
    tang = tang./sum(tang);
    
    en = entr(t);
    enang = entr(tang);
    en = en+0.5*enang;
    if en>bestent(end)
        bestent(end+1) = en;
        bestix = ix;
        fprintf('new best: %.2f / 5.46 \n',en)
    end
    if en > 5.46
        break
    end
    
end
ix_out = [25 ix];
if 1 == 0
    %%
ix = bestix;

xx2 = xx([25 ix]);
yy2 = yy([25 ix]);

di = sqrt(diff(xx2).^2 + diff(yy2).^2);
diang = atan2(diff(xx2),diff(yy2));

t = histc(di,edgesangle);
tang = histc(diang,edgesangle);

t = t./sum(t);
tang = tang./sum(tang);

    
en = entr(t);
enang = entr(tang);
% 
subplot(3,2,1)
histogram(di,edges)
subplot(3,2,3)
histogram(di,0.5:1:30)
subplot(3,2,5)
histogram(di,0:0.1:30)

subplot(3,2,2)
histogram(diang,edgesangle)
subplot(3,2,4)
histogram(diang,-pi:1:pi)
subplot(3,2,6)
histogram(diang,-pi:0.1:pi)

%% plot trajectory
figure
for k = 1:length(ix)
    hold off
    % grid
    plot(xx,yy,'ob')
    hold on
    %already visited
    plot(xx2(1:k),yy2(1:k),'og')
    %individual
    
    plot(xx2(k:k+1),yy2(k:k+1),'r-')
    pause()
    
end

end