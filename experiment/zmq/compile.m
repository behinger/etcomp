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
    mex zmq_subscriber.c utils.c multi_connector.c -lczmq -lzmq
    mex zmq_request.c utils.c multi_connector.c -lzmq
    -O CFLAGS="\$CFLAGS -std=c99" -I"/net/home/student/i/iibs/build_custom/include" -L"/net/home/student/i/iibs/build_custom/lib/" -l"/net/home/student/i/iibs/build_custom/lib/zmq" 
end
