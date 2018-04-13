% test skript pupil labs
zmqpath = 'zmq/';
%addpath(genpath(stimpath)) 
addpath(genpath(zmqpath)) 
zmq_request('init');
requester = zmq_request('add_requester', 'tcp://localhost:37175');
requester = int32(requester);
reply = sendETNotifications('Connect Pupil', requester);
% sendETNotifications('R',requester)
% data  = struct('soup',3.57,'bread',2.29,'bacon',3.91,'salad',5.00);
% ser_data = serialize(data)
% bytes = dumpmsgpack(data);


sendETNotifications(['notify logging.warning test'],requester)

