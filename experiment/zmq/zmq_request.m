% zmq_request  ZeroMQ requester.
%    zmq_request('INIT')
%    Initializes ZeroMQ.
%
%    requester_id = zmq_request('ADD_REQUESTER', end_point)
%    Adds a requester (see example below).
%
%    zmq_request('SEND_REQUEST', requester_id, message)
%    Sends a request. The message must be a string.
%
%    message = zmq_request('RECEIVE_REPLY', requester_id, timeout)
%    Receives the reply. The return value is the message as a string, or NaN.
%    If after 'timeout' milliseconds there is still no messages available, NaN
%    is returned. If 'timeout' is 0, this function doesn't block. With a long
%    timeout, a NaN return value can mean that the replier is not connected. To
%    block until a message is available, set a timeout of -1.
%
%    zmq_request('CLOSE')
%    Closes all requesters, to free resources. It is important to call this
%    function when the requesters are no longer needed. Otherwise problems can
%    occur, especially after running several times the same script.
%
%    Example:
%    zmq_request('init');
%    requester = zmq_request('add_requester', 'tcp://localhost:5555');
%
%    zmq_request('send_request', requester, 'foo');
%    reply = zmq_request('receive_reply', requester, 3000)
%
%    zmq_request('close');
%
% Sébastien Wilmet, 2015.
