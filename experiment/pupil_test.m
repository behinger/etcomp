% test skript pupil labs
zmqpath = 'zmq/';
%addpath(genpath(stimpath)) 
addpath(genpath(zmqpath)) 
zmq_request('init');
requester = zmq_request('add_requester', 'tcp://localhost:50020');
requester = int32(requester);
reply = sendETNotifications('Connect Pupil', requester);
sendETNotifications('R',requester)
data = {'notify life'};
ser_data = serialize(data)
bytes = dumpmsgpack(ser_data);
%sendETNotifications(data,requester)

