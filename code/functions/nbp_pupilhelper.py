
  
def gaze_to_pandas(gaze):
        # Input: gaze data as dictionary
        # Output: pandas dataframe with gx, gy, confidence, time of pupillabsdata
        import pandas as pd
        
        list_diam= []
        for idx,p in enumerate(gaze):
            if p:
               # take the mean over all pupil-diameters
               diam = 0
               for idx_bd,bd in enumerate(p['base_data']):
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
        
        
        
        
            
                