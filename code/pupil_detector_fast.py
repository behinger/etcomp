# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 11:43:50 2020

@author: Janis Keck
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 16:07:18 2020

@author: Janis Keck
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 18:19:29 2020

@author: Janis Keck
"""
import functions.add_path

import functions.plotnine_theme

from plotnine import *
from plotnine.data import *

import cv2
import eyerec 
import os
import numpy as np
import pandas as pd
import file_methods as fm

import av # import to import before any pupillabs libraries
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
    import lib.pupil.pupil_src.shared_modules.calibration_routines.manual_marker_calibration as mc

except Exception as e:
    print('-------------------')
    print(e)
    pass
tryimport, builtins.__import__ = builtins.__import__, realimport
import pl_anna_tools

from functions.et_helper import tic,toc




def normalize(pos, size, flip_y=False):
    """
    normalize return as float
    """
    width,height = size
    x = pos[0]
    y = pos[1]
    x /=float(width)
    y /=float(height)
    if flip_y:
        return x,1-y
    return x,y



def detect_pupils(detector_type,outputpath,path_to_data):
    ''' Detects pupils in video & writes the result to pldata file
        
        args:
             detector_type - str, which eyerec-detector to use, must be one of ['PuRe','PuReSt'] (afaik case-insensitive)
             outputpath - str, path, where to write data
             path_to_data - str, path, path where to find video & npy files 
        
        returns: 
             None, writes 'pupil.pldata' and 'pupil_timestamps.npy' '''
    
    
    os.chdir(path_to_data)

    writer = fm.PLData_Writer(outputpath, 'pupil')
    for eyeid in [0,1]: 
                        # set up pupil detector
                        detector = eyerec.PupilTracker(name=detector_type)

        
        
                        # load timestamps - we reuse the timestamps that are already there, we assume these are the correct ones

                        timestamps = np.load('eye{}_timestamps.npy'.format(str(eyeid)))
        
                        video = 'eye{}.mp4'.format(str(eyeid))
        
                        # TODO: cv2 is only used here to get the framenr of the video, replace this by corresponding method of pl_anna_tools
                        vidcap = cv2.VideoCapture(video)
    
                        #imgs = video2imgs('eye0.mp4')
                       
                        #get number of frames in video
                        Nframes = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        
                        #success = True
                        #initate video
                        cap = pl_anna_tools.init_playback(video_name = video,video_file_path = path_to_data)
        
        
                        for framenr in range(Nframes):
            
                            if (framenr%1000 ==0): print('currently detecting pupil at time ',timestamps[framenr])
            
                            #vidcap.set(cv2.CAP_PROP_POS_FRAMES,framenr)

                            cap.seek_to_frame(framenr)
                             
                            try: 
                                frame= cap.get_frame() 
                                success=True
                            except:
                                success = False
                                print('Error with frame nr ',framenr)
                            #success,image = vidcap.read()
            
            
                            if success:
                                
                                #get frame and timestamp
                                timestamp = timestamps[framenr]
                                #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                                gray = frame.gray
                                # get image shape (for normalization)
                                height = gray.shape[0]
                                width = gray.shape[1]
                                
                                # detect pupils
                                pupil = detector.detect(timestamp,gray)
               
               
                                result = {}
                                if pupil is not None:

                                    # create a subdictionary with ellipse parameters in analogy to the pupil-methods
                                    keymap = {'angle':'angle','size':'axes','center':'center'}
                                    result['ellipse']={keymap[key]: pupil[key] for key in ['angle','size','center']}
                                     #add confidence value as separate item
                                    result['confidence']=pupil['confidence']
                                    # add id and timestamp information
                                    result['id'] = eyeid
                                    result['timestamp']=timestamp
                                    # compute norm_center as in 2d method
                                    norm_center = normalize( result['ellipse']['center'] , (width, height),flip_y=True)
                                    result['norm_pos']=norm_center
                
                                    # for now we fake that these results were from the 2d detector
                                    result['method']='2d c++'
                                    result['true_method']=detector_type
                
                
                                    # add diameter of pupil for later functions
                                    result['diameter'] = max(result['ellipse']['axes'])
                                    #add topic

                                    result['topic']= 'pupil.{}'.format(str(eyeid))
               
               
               
                                    writer.append(result)
               
                
    writer.close()            
                
        
    








if __name__ == '__main__':
    
    path = '/net/store/nbp/projects/IntoTheWild/ET_Analysis/pupil_detection'
    redetect = False # set to True if redetecting already detected data (with this script) is intended
    os.chdir(path)
    
    #table of relevant sessions
    subject_table = pd.read_table('relevantETfiles.txt',sep=',',index_col=0,header=0)
    
    #where to find the data
    datapath = '/net/store/nbp/projects/IntoTheWild/Daten/Eyetracking/Wild/'
    
    #where to store the data
    outpath = os.path.join(path,'detected_data')
    
    
    if not os.path.exists(outpath):
        os.makedirs(outpath)
        
    
    
    for ind in subject_table.index:
        subject = 'VP' + str(ind)
        
        for session in ['ET1','ET2','ET3','ET4']:
            
            session_id = subject_table.loc[ind,session]
            
            ## 99 codes for not relevant session
            if session_id ==99:
                continue
            
            else:
                
                postfix= '00'+str(session_id)
                print('Currently processing ' + subject + 'session ' + postfix + '\n')

                tic()
                #create output path
                for detector_type in ['PuRe','PuReSt']:
                    #if detector_type == 'PuReSt':
                     #   redetect = True
                    outputpath = outpath
                    # next loop is overly complicated because I thought makedirs wasn't working correctly...
                    for joined in [subject,postfix,detector_type]:
                        
                        outputpath = os.path.join(outputpath,joined)

                    
                        if not os.path.exists(outputpath):
                            os.makedirs(outputpath)
                            print('created path ',outputpath)
                    if (redetect == False) & (os.path.isfile(os.path.join(outputpath,'pupil.pldata'))):
                                              continue
                                              
                    

                    
                    current_datapath = os.path.join(datapath,subject,postfix)
                    
                    detect_pupils(detector_type,outputpath,current_datapath)
                    print('Data written for subject ',subject,' session', postfix, ' using ',detector_type)

                toc()