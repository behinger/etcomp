function [reply ] = sendETNotifications(msg, requester)

zmq_request('send_request', requester, msg);
reply = zmq_request('receive_reply', requester, 1000);

if isnan(reply)
    warning('Could not receive message from pupillabs, please connect')
end

% %%% python code for notifications
%     def notify(notification):
%         """Sends ``notification`` to Pupil Remote"""
%         topic = 'notify.' + notification['subject']
%         payload = serializer.dumps(notification, use_bin_type=True)
%         socket.send_string(topic, flags=zmq.SNDMORE)
%         socket.send(payload)
%         return socket.recv_string()
% 
%     def send_trigger(label, timestamp, duration=0.):
%         return notify({'subject': 'annotation', 'label': label,
%                       'timestamp': timestamp, 'duration': duration,
%                       'source': 'example_script','record': True})
% 
%     # Start the annotations plugin
%     notify({'subject': 'start_plugin',
%             'name': 'Annotation_Capture',
%             'args': {}})
