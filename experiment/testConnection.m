function [] = testConnection(eyetracking, requester)
elapsedTimes = [];
for i=1:1000
    tic
    sendETNotifications(eyetracking,requester,sprintf('Trigger %d', i));
    elapsedTimes(i) = toc;
end


save('delayedTriggers.mat','elapsedTimes')