%% How to compile
% ZMQ is already installed on the computer
% You have to start matlab using:
%
% LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab
%
% Else it wont work


if strcmp (computer (), 'PCWIN')
    % Under Windows:
    % It doesn't work well when the DLL is not in the same directory as the
    % generated mex file. Maybe because there are spaces in the path to the
    % installed DLL?
    mex zmq_subscriber.c utils.c multi_connector.c ...
        -I"C:\Program Files\ZeroMQ 4.0.4\include" ...
        -L"C:\Program Files\ZeroMQ 4.0.4\lib" ...
        -llibzmq-v90-mt-4_0_4

    mex zmq_request.c utils.c multi_connector.c ...
        -I"C:\Program Files\ZeroMQ 4.0.4\include" ...
        -L"C:\Program Files\ZeroMQ 4.0.4\lib" ...
        -llibzmq-v90-mt-4_0_4
else
    % Under GNU/Linux:
    try
    mex zmq_request.c utils.c multi_connector.c -lzmq 
    catch
        
    error('maybe forgot to start matlab using LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab, or maybe did not install zeromq?')
    end

end
