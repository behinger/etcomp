import pandas as pd
import numpy as np
import functions.detect_events as detect_events
import functions.et_helper as helper
from functions.et_helper import winmean_cl_boot

import functions.et_condition_df as condition_df
import logging
from plotnine import *

# specify costumed minimal theme
import functions.plotnine_theme as mythemes

logger = logging.getLogger(__name__)

import MISC

def detect_microsaccades(etsamples,etevents,etmsgs,engbert_lambda=5):
    all_microsaccades = pd.DataFrame()
    
    for subject in etmsgs.subject.unique():
        for eyetracker in etmsgs.eyetracker.unique():
            for block in etmsgs.block.dropna().unique():
                if block < 1:
                    continue
                print('block:%s,subject%s,eyetracker%s'%(block,subject,eyetracker))
                query = 'subject==@subject&eyetracker==@eyetracker'
                logger.info(query.format())

                # select the start / end triggers of the microsaccade blocks

                sel_etmsgs = etmsgs.query(query+ "&block==@block&condition=='MICROSACC'&exp_event=='start'")
                starttime = etmsgs.query(query+"&block==@block&condition=='MICROSACC'&exp_event=='start'").msg_time.values
                endtime = etmsgs.query(query+"&block==@block&condition=='MICROSACC'&exp_event=='stop'").msg_time.values

                # find which samples belong into that timeframe
                sel_etsamples = etsamples.query(query)
                #is_microsaccade = helper.eventtime_to_sampletime(sel_etsamples,starttime,endtime)
                
                # set these to 1 so that we can select them
                #sel_etsamples.loc[sel_etsamples.index[is_microsaccade],'microsaccade'] = 1
                # overwrite the previous detected types, so that we can fill in the microsaccade types
                #sel_etsamples.loc[:,'type'] = np.nan

                #sel_etsamples = sel_etsamples.query("microsaccade==1")
                sel_etsamples = sel_etsamples.query("smpl_time>@starttime&smpl_time<@endtime")
                engbert_lambda  = engbert_lambda
                if sel_etsamples.shape[0]<1:
                    logger.warning('No samples found')
                    continue
                # Run the microsaccade detection
                try:
                    sel_etsamples,sel_etevents = detect_events.make_saccades(sel_etsamples,etevents=None,et=eyetracker,engbert_lambda = engbert_lambda)
                except AttributeError:
                    logger.warning('no microsaccades found')
                    continue
                # fill in some details
                sel_etevents = sel_etevents.assign(subject=subject)
                sel_etevents = sel_etevents.assign(eyetracker=eyetracker)
                sel_etevents = sel_etevents.assign(block=block)

                # remove all saccades larger than amplitude of 2
                logger.info("Removed %i saccades larger than amplitude 2°"%(np.sum(sel_etevents.amplitude>2)))
                sel_etevents = sel_etevents.query("amplitude<2")

                # Match which saccades belong to which blocks

                #microsaccade = condition_df.get_condition_df(data=(sel_etsamples,sel_etmsgs,sel_etevents),condition="MICROSACC")
                
                all_microsaccades = pd.concat([all_microsaccades, sel_etevents])
    return(all_microsaccades)

def group_microsaccades(microsaccades):
    from functions.et_helper import winmean
    microsaccades_grouped = microsaccades.groupby(["eyetracker","subject"],as_index=False).agg({'amplitude':['count',winmean]})
    microsaccades_grouped.columns = [' '.join(col).strip() for col in microsaccades_grouped.columns.values]
    microsaccades_grouped = microsaccades_grouped.rename(index=str,columns={"amplitude count":"count"})
    print(microsaccades_grouped.columns)
    return(microsaccades_grouped)



def plot_default(microsaccades,subtype="count"):
    
    # subtype can be "count"  or "mean"
    microsaccades_grouped = group_microsaccades(microsaccades)
           
    p = (ggplot(microsaccades_grouped,aes(x="eyetracker",y=subtype))
        + geom_line(aes(group='subject'), color='lightblue')
        + geom_point(alpha=0.9, color='lightblue')
        + stat_summary(fun_data=winmean_cl_boot, color='black', size=0.8, position=position_nudge(x=0.05,y=0))
        + xlab("Eye Trackers")
        + ggtitle('Microsaccades'))
    
    
    MISC.print_results(microsaccades_grouped, fields = ['count', 'amplitude winmean'], agg_first_over_blocks=False,round_to=2)

    return p



def plot_densities(microsaccades,x="amplitude"):
    p = (ggplot(microsaccades,aes(x=x))
         +geom_density(aes(group="subject"),alpha=0.3)
         +geom_density(color='red',size=2)
         +facet_grid("eyetracker~.",scales="free_y")
        )
    return(p)

def plot_mainsequence(microsaccades):
    p = (ggplot(microsaccades,aes(x="np.log10(amplitude)",y="(peak_velocity)"))
         +geom_point(aes(color="subject"),alpha=0.1)
         #+stat_smooth(size=2,color="red",method="loess")
         +facet_grid("eyetracker~.")
        )
    return(p)

