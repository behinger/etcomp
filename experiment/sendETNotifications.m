function [reply ] = sendETNotifications(eyetracking,requester,msg)
% Function to send messages to both eyetrackers at the same time. requires
% cosymatlab - zmq. and the eyelink libraries
assert(ischar(msg),'message is not a string')

if eyetracking
    % send to eyelink
    Eyelink('message',msg);
    
    % send to pupillabs via zmq and nbp-custom plugin
    zmq_request('send_request', requester, msg);
    reply = zmq_request('receive_reply', requester, 1000);
    
    if isnan(reply)
        warning('Could not receive message from pupillabs, please connect')
    end
else
    fprintf('The following message was NOT send: \n')
    fprintf(msg)
    fprintf('\n')
end

