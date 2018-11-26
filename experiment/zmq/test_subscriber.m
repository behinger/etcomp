clear all;

zmq_subscriber('init');

subscriber1 = zmq_subscriber('add_subscriber', 'tcp://localhost:5000');
zmq_subscriber('add_filter', subscriber1, 'filter1');

subscriber2 = zmq_subscriber('add_subscriber', 'tcp://localhost:5001');
zmq_subscriber('add_filter', subscriber2, 'filter2');

msg = zmq_subscriber('receive_next_message', subscriber1, 0)
msg = zmq_subscriber('receive_next_message', subscriber1, 0)
msg = zmq_subscriber('receive_next_message', subscriber1, 3000)

msg = zmq_subscriber('receive_next_message', subscriber2, 3000)
msg = zmq_subscriber('receive_next_message', subscriber2, 2000)
msg = zmq_subscriber('receive_next_message', subscriber2, 1000)

zmq_subscriber('close');
