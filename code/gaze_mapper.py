# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 12:04:59 2020

@author: Janis Keck
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:34:54 2020

@author: Janis Keck
"""

import os
import functions.add_path

import functions.plotnine_theme
import pandas as pd
import numpy as np
import types
import matplotlib.pyplot as plt
from plotnine import *
from plotnine.data import *
import os
print(os.getcwd())
os.chdir('/net/store/nbp/projects/IntoTheWild/ET_Analysis/pupil_detection/etcomp/code')

import av # import to import before any pupillabs libraries

import file_methods as new_file_methods
from lib.pupil.pupil_src.shared_modules import file_methods as pl_file_methods
from functions import et_import
import functions.nbp_recalib as rc
import av
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
    import lib.pupil.pupil_src.shared_modules.calibration_routines.manual_marker_calibration as mc

except Exception as e:
    print('-------------------')
    print(e)
    pass
tryimport, builtins.__import__ = builtins.__import__, realimport
import pl_anna_tools

from functions.et_helper import tic,toc


   
class Global_Container():
    pass
        
        


def make_format_compatible(dict_iterable):
        ''' This is a workaround to make data generated in the pupil_detector file amenable to 
        the save_object routine. Somehow, the data generated with the new 'filemethods.py'
        by pupil labs turns dictionaries in either SerializedDict which is not a subclass of
        dict but has keys, or _FrozenDict, which is a subclass of dict but can not be manipulated.
        
        Here, we turn all members of these classes and all subdictionaries and so on into normal dicts. 
        (maybe there is some easier way here, but this works)
        
        args:
            dict_iterable - iterable of dictionary-likes
        
        returns:
            list_of_dicts - list, every dictionary- like in the iterable and therin all dicionary-likes turned to dict.
        '''
            
        def key_tryer(ob):
            try:
                ob.keys()
                return True
            except:
                return False
        def base_dicter(dic):

            if (isinstance(dic,dict)) | (key_tryer(dic)):
                dic = dict(dic)
                for k in dic.keys():
        
                    if isinstance(dic[k],dict):
                        dic[k]=base_dicter(dic[k])
            
            return dic            

        list_of_dicts = [base_dicter(datum) for datum in dict_iterable]
        
        return list_of_dicts



def adjust_calibrations(pupil_positions,notifications,time_tolerance=50):
        ''' 
        This adjusts the calibrations in two ways:
            1. strips out all calibrations where the timestamp is out of the timerange of the pupil_data
               (this is because every notifications data has some weird calibration in them where we do not know
               yet where they come from, that does not fall in the correct timerange)
            2. changes the pupil lists from the remaining, correct calibration (i.e. the first one) to the pupil data
               that is newly detected (as these notifications still come from the recording itself)
        
        args:
            pupil_positions - iterable of dicts, should be the pupil_positions from new detection
            notifications   - iterable of dicts, should come from the original recording
            tolerance - numerical, tolerance value for the timestamps of calibrations to be in range
                                   i.e. (min-time_tolerance,max + time_tolerance), arbitrary default 50
        
        returns
            notifications - list of dicts, with weird calibration data removed & pupil lists replaced
           
        '''
        
        # get timestamps & ids
        pupil_timestamps = np.array([p['timestamp'] for p in pupil_positions])
        pupil_ids = np.array([p['id'] for p in pupil_positions])
        
        # remove the weird timestamps
        remove_indices =[]
        for n in range(len(notifications)):
            note = notifications[n]
            
            
            # check if in range
            if (note['timestamp'] < min(pupil_timestamps) - time_tolerance) | (note['timestamp'] > max(pupil_timestamps) + time_tolerance):
                 remove_indices +=[n]
        # remove weird timestamps
        notifications = [notifications[n] for n in range(len(notifications)) if n not in remove_indices]
        print('Removed {} notifications because their timestamp was out of range'.format(str(len(remove_indices))))
        
        # adjust pupil_lists
        for note in notifications:
                       
            if note['subject'] == 'calibration.calibration_data':
                plist = note['pupil_list']
                plist_new = []
                for p in plist:
                    ts = p['timestamp']
                    id = p['id']
                    matched_idx = ((pupil_timestamps==ts)&(pupil_ids==id)).nonzero()[0]
                    
                    # sanity check: should have exactly one match 
                    assert len(matched_idx)==1,'Found {} pupil positions for id {} found at timestamp {} , aborting'.format(str(len(matched_idx)),str(id),str(ts))
                    plist_new += [pupil_positions[matched_idx[0]]]
                note['pupil_list']=plist_new

        print('calibrations adjusted')
        return notifications
    
    
    
def load_and_adjust(path_to_new_pupil_data,video_file_path,save=False,outname = 'pupil_data_calibrations_adjusted',datapath = None):
        ''' load new pupil detection data & old notification data,
            adjust calibrations, put everything into one dictionary, & return 
        
        args :
            path_to_new_pupil_data - str, path, where the new detected pupil data is stored
            video_file_path - str,path, where the original data (video files, but also timestamps), can be found
            
            save - boolean, default True, whether adjusted data should be saved
            outname - str, filename if to be saved
            datapath  - str, path, where to save file, defaults to path_to_new_pupil_data
            
        returns:
            pupil_data - dict, keys: pupil_positions,gaze_positions,notifications
            '''
        
    
        pl_data = new_file_methods.load_pldata_file(path_to_new_pupil_data,topic='pupil')
        
        newpupil_data = new_file_methods.load_object(os.path.join(video_file_path,'pupil_data'))
     
    
        notifications = newpupil_data['notifications']
        
        pupil_positions = list(pl_data.data)


        # on the highest level we actually want a list of dicts
        pupil_positions = make_format_compatible(pupil_positions)

        notifications = make_format_compatible(notifications) 

        
        #strip weird calibrations & adjust pupil data
        
        notifications = adjust_calibrations(pupil_positions,notifications)
        
        
        
        
       
        

        pupil_data = {'pupil_positions':pupil_positions,'gaze_positions':[],'notifications':notifications}

       
        if save:
            
            if datapath is None:
                datapath = path_to_new_pupil_data
        
        
            pl_file_methods.save_object(pupil_data,os.path.join(datapath, outname))
            
        

        
        return pupil_data

def find_calibration_markers(pupil_data,video_file_path,calibration_ranges,save=False,outname = 'pupil_data_new_calibrations_added',datapath = None):
    
        ''' load data, find calibration markers & append to data
        
        
        args :
            pupil_data - dict, keys: pupil_positions,gaze_positions,notifications 
            video_file_path - str,path, where the original data (video files, but also timestamps), can be found
            calibration_ranges - iterable, every item should be of the form [start_calibration,end_calibration]
                                 a list of indices indicating when the calibration started & ended
            
            save - boolean, default True, whether adjusted data should be saved
            outname - str, filename if to be saved
            datapath  - str, path, where to save file
            
        returns:
           pupil_data - dict, same as above, with new calibrations appended to notifications
                 
                  
        '''
        
    
        
        
        cap = pl_anna_tools.init_playback(video_name = 'world.mp4',video_file_path = video_file_path)
        
        
        
        
        #get timebins of world timestamps that correspond to pupil timestamps
        world_timestamps= np.load(os.path.join(video_file_path,'world_timestamps.npy'))

        ind = np.digitize([p['timestamp'] for p in pupil_data['pupil_positions']],world_timestamps)-1


    
        for calibration_range in calibration_ranges:
            calib = mc.Manual_Marker_Calibration(Global_Container)

            # we cant use the calib.start() because of the super-inherited function that wants to update the gui
           
            calib.active = True
            calib.ref_list = []
            calib.pupil_list = []
            calib.button = Global_Container()
            calib.g_pool.get_timestamp = lambda:None
            calib.trackerid = 0
            def notify_capture_complete(self,x):
                #print(x)
                if x['subject'] == 'calibration.marker_sample_completed':
                    self.trackerid +=1
                    print(self.trackerid)
                    for i,r in enumerate(self.ref_list):
                        if 'trackerid' not in r.keys():
                            r['trackerid'] = self.trackerid
                        self.ref_list[i] = r
                else: print(x['subject'])



            calib.notify_all =  types.MethodType(notify_capture_complete,calib)
            calib.button = Global_Container()
            calib.button.status_text = ''
            calib.notify_all({'subject':'test'})
            #print('index',sub_ind)
            
            #selection of the respective calibration range in the dataframe
            
            a = calibration_range[0]
            b = calibration_range[1]
            
            
            #a=int(calib_frames.loc[sub_ind, num+pos])
            #b=int(calib_frames.loc[sub_ind, num+pos+1])
            print('now calibration for range:')
            print(a)
            print(b)
            
            calibrange = range(a,b)
            calib.circle_tracker._wait_count = 0
            tic()
            for k in calibrange:
                if np.mod(k-min(calibrange),500) == 0:
                    print('Progress: %.1f%%'%((float(k-min(calibrange))/(max(calibrange)-min(calibrange)))*100))

                cap.seek_to_frame(k)

                frame= cap.get_frame()

                #print(frame.gray.shape, 'shape')

           
                pupil_idx = np.where(ind == cap.get_frame_index())[0]
                pupil_in_bound = [dict(pupil_data['pupil_positions'][i]) for i in pupil_idx]
               
                
                
                calib.recent_events({'frame':frame,'pupil':pupil_in_bound,'pupil_positions':pupil_in_bound})
                
            toc()
            print('ref_list len ',len(calib.ref_list))
            
            #continue statement einbauen, falls keine targets gefunden. dann print nothing found
            if all('trackerid' in note.keys() for note in calib.ref_list) and len(calib.ref_list) > 1:

                #trackerids = [r['trackerid'] for r in calib.ref_list]

                # for jedes trackerid timestamp set, find pupil positions that fall into that set


                new_result = {'calibration_method':'2d','record':'true','timestamp': calib.ref_list[-1]['timestamp'], 'pupil_list': calib.pupil_list, 'ref_list': calib.ref_list, 'subject': 'calibration.calibration_data' }
                pupil_data['notifications'].append(new_result)
                print('Added new calibration data to notifications')
                print('timestamp:',new_result['timestamp'])
                calib=[]
            
            else:
                print('No markers found, skipping this Video')
                calib=[]
                pass     
            
            
        if save:
            try: 
                os.path.exists(datapath)
                pl_file_methods.save_object(pupil_data,os.path.join(datapath, outname))
            except: print('If you want to save data, please provide valid path')
                    
         

        return pupil_data
    
    
    
def calculate_gaze_mappings(pupil_data):
        ''' calculates gaze mappings for calibrated data via nbp_recalib.
        
            args:
                pupil_data - dict, keys: pupil_positions,gaze_positions,notifications
                
            returns:
                pupil_data - dict, as above, but gaze_positions appended with newly computed ones from calibrations
        '''
    
        print('Calculating gaze mappings....')

      
        
        recalib_data = rc.nbp_recalib(pupil_data, calibration_mode='2d', eyeID=None)                
       
        print('Old length: ',len(pupil_data['gaze_positions']))
        print('New length: ', len(recalib_data))
       
        pupil_data['gaze_positions'] = recalib_data

        return pupil_data
    
    
    
def save_data(pupil_data,datapath,old=True,new=True):
        ''' Saves pupil data to file, using old and or new file methods.
    
    
        args:
            pupil_data - dictionary, keys: pupil_positions,gaze_positions,notifications
        
            datapath - str, path, where to save
        
            old - boolean, default True, if True saves in old format in datapath
        
            new -boolean, default True, if True saves
             'topic.pldata','topic_timestamps.npy' for topic in ['pupil','gaze','notify']
              in datapath/new_gaze_mappings in new file format
              (implicit sanity check: pupil.pldata in this path should be the same as the new pupil detected data)
        '''
    
        if old:
            pl_file_methods.save_object(pupil_data,os.path.join(datapath, 'pupil_data_new'))
        
        if new:
            if not os.path.exists(os.path.join(datapath,'new_gaze_mappings')):
                os.makedirs(os.path.join(datapath,'new_gaze_mappings'))
            outputpath = os.path.join(datapath,'new_gaze_mappings')
            pupil_writer = new_file_methods.PLData_Writer(outputpath, 'pupil')
        
            pupil_writer.extend(pupil_data['pupil_positions'])
            pupil_writer.close()
            
            gaze_writer = new_file_methods.PLData_Writer(outputpath, 'gaze')
        
            gaze_writer.extend(pupil_data['gaze_positions'])
              
            gaze_writer.close()
            note_writer = new_file_methods.PLData_Writer(outputpath, 'notify')
            # new file methods need notifications to have a topic
            for p in pupil_data['notifications']:
               p['topic'] = 'notify'+'.'+p['subject']
               note_writer.append(p)
            
            note_writer.close()
          
        
        
        print('Data saved to folder')











































if __name__ == '__main__':
    

    remap = False

    mypath = '/net/store/nbp/projects/IntoTheWild/ET_Analysis/pupil_detection/detected_data/'



    calib_file='/net/store/nbp/users/yschwarze/nbp_intothewild/Analysis/Eyetracking/calib_ranges.csv'



    calib_frames = pd.read_csv(calib_file,sep=",",index_col=0,header=None,skiprows=[0,6])
    calib_frames = calib_frames.loc[calib_frames.index.dropna(),:]
    calib_frames.index = calib_frames.index.astype(int)
    calib_frames = calib_frames.fillna('')



#import sys
#table of relevant sessions
    print(os.getcwd())
    os.chdir('/net/store/nbp/projects/IntoTheWild/ET_Analysis/pupil_detection/etcomp/code')

    subject_table = pd.read_table('relevantETfiles.txt',sep=',',index_col=0,header=0)
    #print(subject_table.index)

    #sys.exit()
    counter=0
    for sub_ind in subject_table.index:
        subject = 'VP' + str(sub_ind)
        
        for session_index in [1,2,3,4]:
        

            session = 'ET'+str(session_index)
            session_id = str(subject_table.loc[sub_ind,session])
            
            ## 99 codes for not relevant session
            if session_id ==99:
                print('no more relevant sessions for this subject')
                continue
        
            postfix= '00'+str(session_id)
        
        
        
        
            if session_index==1:
                pos=2
            elif session_index==2:
                pos=8
            elif session_index==3:
                pos=14
            elif session_index==4:
                pos=20
        
        
        
        
        
        
        
            video_file_path=os.path.join('/net/store/nbp/projects/IntoTheWild/Daten/Eyetracking/Wild/',subject,postfix)
        
        
        
            for detector_type in ['PuRe','PuReSt']:

                print('currently working on ', subject, ' ', session, ' ','detector type ',detector_type)

        
                datapath = os.path.join(mypath,subject,postfix, detector_type)
        
                if not os.path.isfile(os.path.join(datapath,'pupil.pldata')):
                    print('Pupils not detected yet')
                    continue

                if (remap==False) & (os.path.isfile(os.path.join(datapath,'new_gaze_mappings','gaze.pldata'))):
                    print('Gaze data has already been calculated for {}. Set remap parameter if you want to  it again'.format(detector_type))
                    continue
        
                path_to_new_pupil_data = datapath
              
                
                if os.path.isfile(os.path.join(datapath,'pupil_data_new_calibrations_added')):
                    pupil_data =  new_file_methods.load_object(os.path.join(datapath,'pupil_data_new_calibrations_added'))

                else:    
                    if os.path.isfile(os.path.join(datapath,'pupil_data_calibrations_adjusted')):
                        pupil_data =  new_file_methods.load_object(os.path.join(datapath,'pupil_data_calibrations_adjusted'))
                    else:
                       pupil_data = load_and_adjust(path_to_new_pupil_data, video_file_path,save=True)
                   
                    
                    #get calibration ranges from dataframe
                     
                    calibration_ranges = [[int(calib_frames.loc[sub_ind, num+pos]),int(calib_frames.loc[sub_ind, num+pos+1])] for num in [0,2]]

                    
                    pupil_data = find_calibration_markers(pupil_data,video_file_path,calibration_ranges,save=True,outname = 'pupil_data_new_calibrations_added',datapath = path_to_new_pupil_data)
    
                pupil_data = calculate_gaze_mappings(pupil_data)
                    
                save_data(pupil_data,datapath)
                    
                    
                

        
        
      
           