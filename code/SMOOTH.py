import numpy as np
import functions.et_helper as helper
import pandas as pd
import sys
import functions.et_make_df as make_df
import traceback
import logging

from plotnine import *
from matplotlib import pyplot as plt
from functions.et_helper import winmean,winmean_cl_boot

logger = logging.getLogger(__name__)

# Helper Functions
def makeRot(theta):
    # Generate a rotation matrix (pretty standard)
    # Input in degree
    theta = np.radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c,-s), (s, c)))
    return(R)

def rotate(gx,gy,theta):
    # rotate  input gx/gy pairs in the direction "theta"
    R = makeRot(theta).T
    out = np.dot(R,[gx,gy])
    return(out)

def rotateRow(row):
    # wraper to "rotate" to be able to use the pandas array
    theta = row.iloc[0].angle
    assert(len(row.angle.unique())==1)
    rot = rotate(row.gx.values,row.gy.values,theta)
    row.loc[:,'rotated'] = rot[0]
    return(row)

def compileModel(modelname ="/net/store/nbp/users/behinger/projects/etcomp/code/changepoint.stan"):
    # compile the bayesian model to c++  (extra function to speed things up by reusing the model)
    import pystan
    return(pystan.StanModel(file=modelname))

def fitTrial(d,sm=None,etevents=None):
    # Estimate the point of onset by a (2-pieces) piecewise regression were the first part has slope 0.
    if not sm:
        # if model does not exist, compile, but should be done before to reduce overhead greatly
        sm = compileModel()
    
    # remove data up to first saccade (i.e. remove data after first saccade)
    try:
        

        # find the first saccade after 100ms
        firstSaccIx = np.where((d.type == "saccade") & (d.td >0.1))[0][0]
    #else:
        allSaccIx = ((d.type == "saccade") & (d.td >0.1))*1
        diffix = np.diff(allSaccIx)
        #0 0 1 0  0 0 1 1 1  1 0 0 1 1 1 1 1 1  1 0 
        #0 0 1 -1 0 0 1 0 0 -1 0 0 1 0 0 0 0 0 -1 0


        saconset = np.where(diffix == 1)[0]
        if saconset.shape[0] == 0:
            firstSaccIx = np.nan #will throw indexerror then
            print('showindexerror')
        else:
            sacoffset = np.where(diffix == -1)[0]

            if sacoffset.shape[0]- saconset.shape[0] == -1: # offset one to short
                sacoffset = np.append(sacoffset,allSaccIx.shape[0]-1)

            sacamplitude  = d.rotated.iloc[sacoffset].values -d.rotated.iloc[saconset].values

            firstSaccIx = saconset[sacamplitude>1] # saccade larger than 1deg
            firstSaccIx = firstSaccIx[0]

            
            
        d = d.iloc[0:firstSaccIx]
        
        
    except IndexError as err:
        logger.error(err)
        logger.error('no saccade found (not a problem)')
        pass
            
    if d.shape[0]<10:
        logger.warning('less than 10 samples, aborting')
        pass
    
    # setup data
    datafit={'ntime': d.shape[0],
    'etdata': d.rotated.values,
    'time':d.td.values,
    'tauprior':.185}
    
    # fit changepoint regression model
    fit = sm.sampling(data=datafit, iter=1500,warmup=300, chains=1)
    
    # return all data, but especially the tau
    return(fit)

def fitTrial_pandas(d,sm,etevents):
    try:
        fit = fitTrial(d,sm,etevents)
    except Exception as err:
        logger.exception('Error smooth model fit single trial'+str(err))
        return(pd.Series({'taumean':np.nan,'taustd':np.nan,'summary':np.nan}))
    return(pd.Series({'taumean':winmean(fit.extract()['tau']),'taustd':np.std(fit.extract()['tau']),'summary':fit.summary(),'velomean':winmean(fit.extract()['slope'])}))


def get_smooth_data(etsamples,etmsgs,select=''):
    
    epochs = make_df.make_epochs(etsamples.query(select),etmsgs.query(select+"&exp_event=='trialstart'&condition=='SMOOTH'"),td=[-0,0.6])
    epochs=  epochs.groupby("angle",group_keys=False).apply(rotateRow)
    return(epochs)
           
def fit_bayesian_model(etsamples,etmsgs,etevents):
    import pystan
    # compile the model
    sm = pystan.StanModel(file="/net/store/nbp/users/behinger/projects/etcomp/code/changepoint.stan")  
    
    smoothresult = pd.DataFrame()
    for subject in etsamples.subject.unique():
        for et in etsamples.eyetracker.unique():
            helper.tic()
            try:
                select = "eyetracker=='%s'&subject=='%s'"%(et,subject)
                epochs = get_smooth_data(etsamples,etmsgs,select)
                
                tmp = epochs.groupby(["trial","block"]).apply(lambda row: fitTrial_pandas(row,sm,etevents))
                smoothresult = pd.concat([smoothresult,tmp.reset_index().assign(eyetracker=et,subject=subject)],ignore_index=True,sort=False)
            except Exception as err:
                logger.critical("error smooth model fit in %s, %s"%(subject,et))
            helper.toc()
    return(smoothresult)
        
def estimate_init_latency(etsamples,etmsgs,etevents):
    smoothresult = fit_bayesian_model(etsamples,etmsgs)
    
    
    
    
def save_smooth(smoothresult,datapath='/net/store/nbp/projects/etcomp/'):
    logger.info('saving...')
    smoothresult.to_csv(datapath+'results/stan_smooth_results.csv')
    logger.info('... saving done')
    
def load_smooth(datapath='/net/store/nbp/projects/etcomp/'):
    smoothresult = pd.read_csv(datapath+'results/stan_smooth_results.csv')
    return(smoothresult)
    
    
    
def plot_single_trial(etsamples,etmsgs,etevents,subject,eyetracker,trial,block,sm):
    select = "subject=='%s'&eyetracker=='%s'"%(subject,eyetracker)
    selectTrial = 'trial==%i&block==%i'%(trial,block)
    etmsgs2 = etmsgs.query(selectTrial)
    epochs = get_smooth_data(etsamples,etmsgs2,select)
    
    out = epochs.query(selectTrial).groupby(["block","trial"]).apply(lambda row:fitTrial(row,sm,etevents))

    fit =out.iloc[0]
    time = epochs.query(selectTrial).td
    def predict(offset,slope,time,tau,autocorr=150):
        w = 1. / (1. + np.exp(-(autocorr*(time-tau))))
        act =  offset +  w *  (slope * (time-tau))#+np.random.normal(0,0.5,len(time))
        return(act)
    def predict_stan(fit,time):
        post =pd.DataFrame(fit.extract())
        if 'autocorrfactor' in post.columns:
            act = post.sample(n=25).apply(lambda row:predict(row.offset,row.slope,time,row.tau,row.autocorrfactor),axis=1)
        else:
            act = post.sample(n=25).apply(lambda row:predict(row.offset,row.slope,time,row.tau),axis=1)
        return(act.values)

    act = predict_stan(fit,time)

    [plt.plot(time,act[i,:],'k',alpha=0.1) for i in range(act.shape[0])]
    plt.plot(time,epochs.query(selectTrial).rotated)
    plt.plot(epochs.query(selectTrial+"&type=='saccade'").td,epochs.query(selectTrial+"&type=='saccade'").rotated,'go')
    plt.plot(winmean(fit.extract()['tau']),0,'ro')
    
    return fit

def plot_modelresults(smoothresult,field="taumean",option=''):
    
    smoothgroup = smoothresult.groupby(['eyetracker','subject'],as_index=False).agg(winmean)
    
    if field == 'taumean':
        binwidth = 0.001
    else:
        binwidth = 0.1
        
    if option == '':
        
         pl = (ggplot(smoothgroup, aes(x='eyetracker', y=field)) +\
                  geom_line(aes(group='subject'), color='lightblue') +
                  geom_point(color='lightblue') +
                  stat_summary(fun_data=winmean_cl_boot,color='black',size=0.8, position=position_nudge(x=0.05,y=0)) +
                  #guides(color=guide_legend(ncol=8)) +
                  xlab("Eye Trackers") + 
                  ylab(field.capitalize()) +
                  ggtitle('Smooth pursuit'))
        
        
    if option=='difference':
        smoothdiff = smoothgroup.groupby("subject").agg(np.diff)
        pl = ggplot(smoothdiff,aes(x=field))+geom_histogram(binwidth=binwidth)+ggtitle('binwidth of %.3f'%(binwidth))
        
    return(pl)

    
def plot_catchup_amplitudes(smooth):
    smooth_saccade = smooth.query("type=='saccade'       & condition=='SMOOTH' & exp_event=='trialstart'") 
    smooth_saccade_agg = smooth_saccade.groupby(["subject","et","block","angle","vel"],as_index=False).agg({'amplitude':winmean})
    smooth_saccade_agg_agg = smooth_saccade_agg.groupby(["subject","et","angle","vel"],as_index=False).agg({'amplitude':winmean})
    
    smooth_saccade_agg_agg.loc[:,'group'] = smooth_saccade_agg_agg['subject'].astype(str) + smooth_saccade_agg_agg['et'].astype(str)
    p = (
        ggplot(smooth_saccade_agg_agg,aes(x="vel",y="amplitude",color="et"))
        #+stat_summary(aes(group='group'),fun_y=winmean,geom='line',linetype='dashed')
        #+stat_summary(aes(group='group'),fun_y=winmean,geom='point')
        +stat_summary(fun_data=winmean_cl_boot)
        
        +ylab('Amplitude of Catchup Saccades')
        )
    
    return(p)