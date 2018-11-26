% zmq_subscriber  ZeroMQ subscriber.
%    zmq_subscriber('INIT')
%    Initializes ZeroMQ.
%
%    subscriber_id = zmq_subscriber('ADD_SUBSCRIBER', end_point)
%    Adds a subscriber (see example below).
%
%    zmq_subscriber('ADD_FILTER', subscriber_id, filter)
%    Adds a filter to an existing subscriber. To receive messages, adding a
%    filter is mandatory. If you want to subscribe to all messages, the filter
%    parameter must be an empty string. (it's exactly how you would do it in C
%    with zmq_setsockopt()).
%
%    message = zmq_subscriber('RECEIVE_NEXT_MESSAGE', subscriber_id, timeout)
%    Receives the next message of a specific subscriber. The return value is
%    the message as a string, or NaN.  If after 'timeout' milliseconds there is
%    still no messages on the queue, NaN is returned. If 'timeout' is 0, this
%    function doesn't block. With a long timeout, a NaN return value can mean
%    that the publisher is not connected. To block until a message is
%    available, set a timeout of -1.
%
%    zmq_subscriber('CLOSE')
%    Closes all subscribers, to free resources. It is important to call this
%    function when the subscribers are no longer needed. Otherwise problems can
%    occur, especially after running several times the same script.
%
%    Example:
%    zmq_subscriber('init');
%
%    subscriber = zmq_subscriber('add_subscriber', 'tcp://localhost:5000');
%    zmq_subscriber('add_filter', subscriber, 'filter');
%
%    msg = zmq_subscriber('receive_next_message', subscriber, 3000)
%
%    zmq_subscriber('close');
%
% Sébastien Wilmet, 2015-2016.
