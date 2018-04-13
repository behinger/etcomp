
  
def gaze_to_pandas(gaze):
        import pandas as pd
        df = pd.DataFrame({'gx':[p['norm_pos'][0] for p in gaze if p],
                           'gy':[p['norm_pos'][1] for p in gaze if p],
                           'time':[p['timestamp'] for p in gaze if p]})
        return(df)