import numpy as np
import pystan
import functions.et_helper as helper
import pandas as pd
import sys
import functions.et_make_df as make_df
import traceback
import logging
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
    import pystan
    return(pystan.StanModel(file=modelname))

def fitTrial(d,sm=None):
    # Estimate the point of onset by a (2-pieces) piecewise regression were the first part has slope 0.
    
    if not sm:
        sm = compileModel()
    
    # remove data up to first saccade (i.e. remove da after first saccade)
    try:
        firstSaccIx = np.where((d.type == "saccade") & (d.td >0.1))[0][0]
        d = d.iloc[0:firstSaccIx]
    except IndexError:
        print('no saccade found')
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

def fitTrial_pandas(d,sm):
    fit = fitTrial(d,sm)
    return(pd.Series({'taumean':np.mean(fit.extract()['tau']),'taustd':np.std(fit.extract()['tau']),'summary':fit.summary()}))


def get_smooth_data(etsamples,etmsgs,select=''):
    epochs = make_df.make_epochs(etsamples.query(select),etmsgs.query(select+"&exp_event=='trialstart'&condition=='SMOOTH'"),td=[-0,0.6])
    epochs=  epochs.groupby("angle",group_keys=False).apply(rotateRow)
    return(epochs)
           
def fit_bayesian_model(etsamples,etmsgs):
    # compile the model
    sm = pystan.StanModel(file="changepoint.stan")  

    smoothresult = pd.DataFrame()
    for subject in etsamples.subject.unique():
        for et in etsamples.eyetracker.unique():
            helper.tic()
            select = "eyetracker=='%s'&subject=='%s'"%(et,subject)
            epochs = get_smooth_data(etsamples,etmsgs,select)
            tmp = epochs.groupby(["trial","block"]).apply(lambda row: fitTrial_pandas(row,sm))
            smoothresult = pd.concat([smoothresult,tmp.reset_index().assign(eyetracker=et,subject=subject)],ignore_index=True,sort=False)
            #except Exception,err:
           #     log.exception('Error smooth model fit')
            #    logger.critical("error smooth model fit in %s, %s"%(subject,et))
            helper.toc()
    return(smoothresult)
        
def estimate_init_latency(etsamples,etmsgs,etevents):
    smoothresult = fit_bayesian_model(etsamples,etmsgs)
    
    
    
    
def save_smooth(smoothresult,datapath='/net/store/nbp/projects/etcomp/'):
    smoothresult.to_csv(datapath+'stan_smooth_results.csv')
    
def load_smooth(datapath='/net/store/nbp/projects/etcomp/'):
    smoothresult = pd.read_csv(datapath+'stan_smooth_results.csv')
    