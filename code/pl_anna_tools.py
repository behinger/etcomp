import av,os

# Pretty serious workaround. Ignores errors in imports :S
import builtins
from types import ModuleType

class DummyModule(ModuleType):
    def __getattr__(self, key):
        return None
    __all__ = []   # support wildcard imports

def tryimport(name, *args, **kwargs):
    try:
        imp = realimport(name, *args,**kwargs)
        #print('success: '+name)
        return imp 
    except Exception as e:
        print('reached exception:' + name)
        if name =='cPickle': # because how they import cPickle/Pickle
            return realimport('pickle', *args,**kwargs)    
        
        #print(e)
        return DummyModule(name)



realimport, builtins.__import__ = builtins.__import__, tryimport
try:
    from video_capture import init_playback_source

except Exception as e:
    print('-------------------')
    print(e)
    pass
tryimport, builtins.__import__ = builtins.__import__, realimport



def init_playback(video_name = 'world.mp4',video_file_path = None):

    class Global_Container(object):
        pass



    cap = init_playback_source(Global_Container(), os.path.join(video_file_path,video_name))
    return(cap)

