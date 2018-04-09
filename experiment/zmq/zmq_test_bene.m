zmq_request('init');
requester = zmq_request('add_requester', 'tcp://100.1.0.3:8000');
requester = int32(requester);

msg = 'r'
zmq_request('send_request', requester, msg);
reply = zmq_request('receive_reply', requester, 1000);
