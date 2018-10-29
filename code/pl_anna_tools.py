import av,os
from video_capture import init_playback_source

def init_playback(video_name = 'world.mp4',video_file_path = None):

    class Global_Container(object):
        pass



    cap = init_playback_source(Global_Container(), os.path.join(video_file_path,video_name))
    return(cap)

