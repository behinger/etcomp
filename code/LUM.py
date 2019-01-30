from plotnine import *
import numpy as np
import pandas as pd
import functions.et_make_df as make_df
from functions.et_helper import winmean,winmean_cl_boot
import MISC
import logging
logger = logging.getLogger(__name__)

def process_lum(etsamples,etmsgs):
    all_lum = pd.DataFrame()
    for subject in etsamples.subject.unique():
        for et in ['pl','el']:
            logger.info("subject:%s, et:%s"%(subject,et))
            all_lum = pd.concat([all_lum,process_lum_singlesub(etsamples,etmsgs,subject,et)])
            
    return(all_lum)

def process_lum_singlesub(etsamples,etmsgs,subject,eyetracker,td=[-1,5]):
    condquery = 'condition == "DILATION" & exp_event=="lum"'
    td = [-1, 12]
    #subject = 'VP1'
    #eyetracker='pl'
    query = 'subject==@subject& eyetracker==@eyetracker'

    lum_epoch = make_df.make_epochs(etsamples.query(query),etmsgs.query(query+'&'+condquery), td=td)

    #normalize by SD division. Could be made better e.g. by quantile division
   
    lum_epoch = lum_epoch.groupby(["msg_time"],as_index=False).apply(lambda rows:standardize_lum(rows))
    #remove duplicated "eyetracker" and "subject" columns
    #lum_epoch = lum_epoch.loc[:,~lum_epoch.columns.duplicated(keep="first")]
    return(lum_epoch)

def standardize_lum(df):
        #df.loc[:,"pa_norm"] = lum_epoch.pa/scipy.stats.iqr(lum_epoch.pa)
        if np.sum(df.td<0)==0:
            logger.warning('trial has no baseline')
            df.loc[:,"pa_norm"] = np.nan
        else:
            df.loc[:,"pa_norm"] = df.pa / np.median(df.loc[df.td<0,'pa'])
        return(df)

def bin_lum(lum_epoch,nbins=100):
    from scipy.stats import binned_statistic
    # to plot the data correctly, we need to bin them & take means
    def lum_bin_function(df):
        newtd = np.linspace(lum_epoch.td.min(),lum_epoch.td.max(),nbins+1)
        binned = binned_statistic(x=df.td,values=df.pa_norm,statistic="mean",bins=newtd)    

        return(pd.DataFrame({"subject":df.subject.iloc[0],"block":df.block.iloc[0],"eyetracker":df.eyetracker.iloc[0],"td":newtd[1:]-(newtd[1]-newtd[0])/2,"pa_norm":binned[0],"lum":df.lum.iloc[0]}))
    
    lum_epoch_binned = lum_epoch.groupby(["subject","eyetracker","lum","block"],as_index=False).apply(lambda rows: lum_bin_function(rows))    
    lum_epoch_binned = lum_epoch_binned.reset_index()
    return(lum_epoch_binned)


def plot_time_all(all_lum_binned):
    # Plot the average over subjects of the average over blocks with +-95CI
    all_lum_binned_noblock = all_lum_binned.groupby(["td","eyetracker","subject","lum"],as_index=False).agg(winmean)
    all_lum_binned_noblock.loc[:,'plot_grouping'] = all_lum_binned_noblock.eyetracker + all_lum_binned_noblock.lum.map(str)
    p = (ggplot(all_lum_binned_noblock.query('lum>0'),aes(x='td',y='pa_norm',group="plot_grouping",color="lum",shape="eyetracker"))
                +stat_summary(fun_data=winmean_cl_boot,position=position_dodge(width=0.06),size=0.2) 
                
                +geom_vline(xintercept=[0,3,10] )
                +scale_color_gradient(low='black',high='lightgray')+xlim((-1,6))
                +scale_shape_manual(values=[">","<"])
    )
    return(p)


def plot_time_diff(all_lum_binned,subject="VP3"):
    # Plot the difference between eyetracker for a single subject
    all_lum_diff = all_lum_binned.groupby(["td","lum","block","subject"],as_index=False).pa_norm.agg(np.diff)
    all_lum_diff.loc[:,'pa_norm'] = pd.to_numeric(all_lum_diff.loc[:,'pa_norm'])
    all_lum_diff.loc[:,'plot_grouping'] = all_lum_diff.block.map(str) + all_lum_diff.lum.map(str)

    
    p=(ggplot(all_lum_diff.query("subject==@subject"),aes(x='td',y='pa_norm',color="lum",group="plot_grouping"))
                +geom_line()
                
                +geom_vline(xintercept=[0,3,10] )
                +scale_color_gradient(low='black',high='lightgray')
                +xlim((-1,6))
                +ylab("Eyetracker difference in pupilsize")
                +scale_shape_manual(values=[">","<"])
    )
    return(p)

def calc_mean(all_lum,t_from=2,t_to=3):
    mean_lum = all_lum.query("td>@t_from & td<=@t_to").groupby(["lum","block","subject","eyetracker","msg_time"],as_index=False).pa_norm.agg(winmean)
    return(mean_lum)

def plot_mean(all_lum):
    mean_lum = calc_mean(all_lum)
    p=(ggplot(mean_lum.query("lum>0").groupby(["lum","subject","eyetracker"],as_index=False).pa_norm.agg(winmean),aes(x="lum",y="pa_norm",shape="eyetracker",color="lum"))
     +stat_summary(fun_data=winmean_cl_boot,position=position_dodge(width=15))
     +geom_point(alpha=0.1)
     +scale_color_gradient(low='black',high='lightgray')
     +scale_shape_manual(values=[">","<"])
    )
    return(p)

def plot_diff(all_lum):
    mean_lum = calc_mean(all_lum)
    diff_lum = mean_lum.query("lum>0").groupby(["lum","block","subject"],as_index=False).pa_norm.agg(np.diff)
    diff_lum.loc[:,'pa_norm'] = pd.to_numeric(diff_lum.loc[:,'pa_norm'])
    
    p = (ggplot(diff_lum,aes(x="subject",y="pa_norm",color="lum",group="lum"))
     +stat_summary(fun_data=winmean_cl_boot,position=position_dodge(width=0.5))
     #+geom_point(alpha=0.2,position=position_dodge(width=0.5))
     +scale_color_gradient(low='black',high='lightgray')
     +ylab('pupil area difference (Eyelink-Pupillabs)[a.u.]')
     #+scale_shape_manual(values=[">","<"])
    )
    return(p)