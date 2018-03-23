% LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 matlab
clear all;

zmq_request('init');

%requesters = [];
%requesters(end + 1) = zmq_request('add_requester', 'tcp://localhost:50020');
requester = zmq_request('add_requester', 'tcp://localhost:50020');

disp('Requesters connected');

requester = int32(requester);

request_msg = 1;


disp('Send request...');
zmq_request('send_request', requester, request_msg);
disp('...done.');

disp('Receive reply...');
reply = zmq_request('receive_reply', requester, 3000);


zmq_request('close');
disp('Closed');
