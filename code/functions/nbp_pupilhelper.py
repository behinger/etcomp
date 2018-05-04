#!/usr/bin/env python3
# -*- coding: utf-8 -*-
  
def gaze_to_pandas(gaze):
        # Input: gaze data as dictionary
        # Output: pandas dataframe with gx, gy, confidence, time of pupillabsdata
        import pandas as pd
        
        list_diam= []
        for idx,p in enumerate(gaze):
            
            if p:
                if 'surface' in gaze[0]['topic']:
                    # we have a surface mapped dictionairy. We have to get the real base_data
                    # the schachtelung is: surfacemapped => base_data World Mapped => base_data pupil
                    p_basedata = p['base_data']['base_data']
                else:
                    p_basedata = p['base_data']
                # take the mean over all pupil-diameters
                diam = 0
                for idx_bd,bd in enumerate(p_basedata):
                   diam = diam + bd['diameter']
                diam = diam/(idx_bd+1)
                
                # df = df.append(
                #         {'gx'        :p['norm_pos'][0],
                #          'gy'        :p['norm_pos'][1],
                #          'confidence':p['confidence'],
                #          'smpl_time' :p['timestamp'],
                list_diam.append(diam)
                
                
        df = pd.DataFrame({'gx':[p['norm_pos'][0] for p in gaze if p],
                           'gy':[p['norm_pos'][1] for p in gaze if p],
                           'confidence': [p['confidence'] for p in gaze if p],
                           'smpl_time':[p['timestamp'] for p in gaze if p],
                           #TODO: did I do this correctly?
                           'diameter':list_diam
                           })
        return(df)
        
        
        
        
            
                