import numpy as np
import pystan
import functions.et_helper as helper
import pandas as pd
import sys
import functions.et_make_df as make_df
import traceback
import logging

from plotnine import *
from matplotlib import pyplot as plt
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

def compileModel(modelname ="changepoint.stan"):
    # compile the bayesian model to c++  (extra function to speed things up by reusing the model)
    import pystan
    return(pystan.StanModel(file=modelname))

def fitTrial(d,sm=None,etevents=None):
    # Estimate the point of onset by a (2-pieces) piecewise regression were the first part has slope 0.
    if not sm:
        sm = compileModel()
    
    # remove data up to first saccade (i.e. remove data after first saccade)
    try:
        
        #if etevents is None:
            # unfortunately we do not have the "amplitude" information of the saccades available. Else we could add a minimal amplitude restriction (to exclude microsaccades)
        firstSaccIx = np.where((d.type == "saccade") & (d.td >0.1))[0][0]
    #else:
        allSaccIx = ((d.type == "saccade") & (d.td >0.1))*1
        diffix = np.diff(allSaccIx)
        #0 0 1 0  0 0 1 1 1  1 0 0 1 1 1 1 1 1  1 0 
        #0 0 1 -1 0 0 1 0 0 -1 0 0 1 0 0 0 0 0 -1 0

        #print(diffix)

        saconset = np.where(diffix == 1)[0]
        if saconset.shape[0] == 0:
            firstSaccIx = np.nan #will throw indexerror then
            print('showindexerror')
        else:
            sacoffset = np.where(diffix == -1)[0]
            #print(saconset)
            #print(sacoffset)
            if sacoffset.shape[0]- saconset.shape[0] == -1: # offset one to short
                sacoffset = np.append(sacoffset,allSaccIx.shape[0]-1)

            sacamplitude  = d.rotated.iloc[sacoffset].values -d.rotated.iloc[saconset].values
            #print(d.rotated.iloc[sacoffset])
            #print(saconset)
            #print(d.rotated)
            #print(sacoffset)
            #print(sacamplitude)
            firstSaccIx = saconset[sacamplitude>1] # saccade larger than 1deg
            firstSaccIx = firstSaccIx[0]
            #print(np.where(diffix!=0)[0])
        
        #print(firstSaccIx)
            
            
        d = d.iloc[0:firstSaccIx]
    except IndexError as err:
        print(err)
        print('no saccade found (not a problem)')
        pass
            
    if d.shape[0]<10:
        print('less than 10 samples, aborting')
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
    return(pd.Series({'taumean':np.mean(fit.extract()['tau']),'taustd':np.std(fit.extract()['tau']),'summary':fit.summary()}))


def get_smooth_data(etsamples,etmsgs,select=''):
    epochs = make_df.make_epochs(etsamples.query(select),etmsgs.query(select+"&exp_event=='trialstart'&condition=='SMOOTH'"),td=[-0,0.6])
    epochs=  epochs.groupby("angle",group_keys=False).apply(rotateRow)
    return(epochs)
           
def fit_bayesian_model(etsamples,etmsgs,etevents):
    # compile the model
    sm = pystan.StanModel(file="changepoint.stan")  

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
    print('saving...')
    smoothresult.to_csv(datapath+'results/stan_smooth_results.csv')
    print('... saving done')
    
def load_smooth(datapath='/net/store/nbp/projects/etcomp/'):
    smoothresult = pd.read_csv(datapath+'results/stan_smooth_results.csv')
    return(smoothresult)
    
    
    
def plot_single_trial(etsamples,etmsgs,etevents,subject,eyetracker,trial,block,sm):
    select = "subject=='%s'&eyetracker=='%s'"%(subject,eyetracker)
    selectTrial = 'trial==%i&block==%i'%(trial,block)
    etmsgs2 = etmsgs.query(selectTrial)
    # temporary fix to align streams
    #if eyetracker=='pl':
    #    print('fixing pupillab camera lag of 40ms (according to pupillabs)')
    #    etmsgs2.loc[:,'msg_time'] = etmsgs2.loc[:,'msg_time']+0.045
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
    plt.plot(np.mean(fit.extract()['tau']),0,'ro')
    #print(np.mean(fit.extract()['tau']))
    return fit

def plot_init_latency(smoothresult,option=''):
    
    smoothgroup = smoothresult.groupby(['eyetracker','subject'],as_index=False).apply(np.mean).reset_index()
    
    if option == '':
        pl = ggplot(smoothgroup,aes(x="eyetracker",y="taumean"))+geom_point(alpha=0.1)+stat_summary(color='red')
    if option=='difference':
        smoothdiff = smoothgroup.groupby("subject").agg({'taumean':{'taudiff':np.diff}})
        pl = ggplot(smoothdiff,aes(x="taumean"))+geom_histogram(binwidth=0.005)+ggtitle('binwidth of 5ms')
        
    pl.draw()
    
    
def plot_catchup_amplitudes(smooth):
    smooth_saccade = smooth.query("type=='saccade'       & condition=='SMOOTH' & exp_event=='trialstart'") 
    smooth_saccade_agg = smooth_saccade.groupby(["subject","et","block","trial","angle","vel"],as_index=False).agg({'amplitude':np.mean})
    return(ggplot(smooth_saccade_agg,aes(x="vel",y="amplitude",color="et"))+stat_summary()+ylab('Number of Catchup Saccades'))