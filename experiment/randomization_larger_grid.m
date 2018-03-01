[xx,yy] = meshgrid(linspace(-10,10,7),linspace(-7,7,7));
xx = xx(:);
yy = yy(:);
entr= @(x)-sum(x(x~=0).*log2(x(x~=0)));

centers = 1:17;
d = diff(centers)/2;
edges = [centers(1)-d(1), centers(1:end-1)+d, centers(end)+d(end)];


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
    t = histc(di,edges);
    t = t./sum(t);
    
    en = entr(t);
    if en>bestent(end)
        bestent(end+1) = en;
        bestix = ix;
        fprintf('new best: %.2f \n',en)
    end
    
    
end
%%
ix = bestix;

xx2 = xx([25 ix]);
yy2 = yy([25 ix]);

di = sqrt(diff(xx2).^2 + diff(yy2).^2);
t = histc(di,edges);
t = t./sum(t);

en = entr(t);

% 
subplot(3,1,1)
histogram(di,edges)
subplot(3,1,2)
histogram(di,0.5:1:30)
subplot(3,1,3)
histogram(di,0:0.1:30)
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

