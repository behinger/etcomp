from functions.et_helper import winmean,winmean_cl_boot
import numpy as np
import pandas as pd

def grid_duration(etmsgs):
    gridlist = ['LARGEGRID_stop','SMALLGG_before_stop','SMALLGG_after_stop']

    x = etmsgs.query('condition=="Instruction"&exp_event in @gridlist').groupby(['subject','eyetracker','block'],as_index=False).msg_time.apply(np.diff).reset_index()

    x[['grid_time_before','grid_time_beforeAfterDiff']] = pd.DataFrame(x.msg_time.values.tolist(), index= x.index)
    x['grid_time_after'] = x.grid_time_before + x.grid_time_beforeAfterDiff


    try:
        x = x.drop('msg_time',axis=1)
    except  KeyError:
        pass
    #x
    def percentile(n):
        def percentile_(x):
            return np.percentile(x, n)
        percentile_.__name__ = 'percentile_%s' % n
        return percentile_
    y = x.groupby('eyetracker').agg([winmean,percentile(5),percentile(95)])
    #y = x.groupby(['eyetracker','subject']).agg(winmean).reset_index().groupby('eyetracker').agg([winmean,percentile(5),percentile(95)])

    y.astype('datetime64[s]')[['grid_time_before','grid_time_after']]
    return(y)


def print_results(df,fields = ['duration','accuracy','rms','sd'], round_to=2, agg_first_over_blocks=True):
    
    import scipy.stats
    
    def percentile(n):
        def percentile_(x):
            return np.percentile(x, n)
        percentile_.__name__ = 'percentile_%s' % n
        return percentile_
    
    if 'eyetracker' in df.columns:
        et = 'eyetracker'
        el = 'el'
        pl = 'pl'
        
    else:
        et = 'et'
        el = 'EyeLink'
        pl = 'Pupil Labs'

    
    if agg_first_over_blocks:
        df_agg = df.groupby([et,'subject','block'],as_index=False).agg(winmean).groupby([et,'subject'],as_index=False).agg(winmean)[[et,'subject']+fields]
    else:
        df_agg = df.groupby([et,'subject'],as_index=False).agg(winmean)[[et,'subject']+fields]
    
    
    tmp_main = df_agg.groupby([et]).agg([winmean,percentile(25),percentile(75)])
    
    
    tmp_el = df_agg.loc[df_agg[et]==el,fields]
    tmp_pl = df_agg.loc[df_agg[et]==pl,fields]
    
    
    
    
    tmp_diff = tmp_el.reset_index(drop=True) - tmp_pl.reset_index(drop=True)
       
    tmp_diff_agg = tmp_diff.agg([winmean_cl_boot])

    roundto = str(round_to)


    for c in tmp_diff_agg.columns.levels[0]:
        diff_tuple = tuple(tmp_diff_agg[c].values[0])
        main_tuple = tuple(tmp_main[c].values[0],) + tuple(tmp_main[c].values[1])
        all_tuple = (c,)+main_tuple + diff_tuple

        printstr = 'For EyeLink the winsorized mean %s was \SI{%.'+roundto+'f}{} (IQR: \SI{%.'+roundto+'f}{} to \SI{%.2f}{}), for Pupil Labs \SI{%.'+roundto+'f}{} (IQR: \SI{%.'+roundto+'f}{} to \SI{%.'+roundto+'f}{}), with a paired difference of \SI{%.'+roundto+'f}{} ($CI_{95}$: \SI{%.'+roundto+'f}{} to \SI{%.'+roundto+'f}{})'
        print(printstr%(all_tuple))
