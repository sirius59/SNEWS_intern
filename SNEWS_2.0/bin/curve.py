##Libraries

import os
import requests as req
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rv_discrete
from astropy.time import Time
from scipy.interpolate import UnivariateSpline

##Core

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file

target_file=os.path.join(file_dir,f'data/fast_slow.csv')
raw_fast_slow=pd.read_csv(target_file)
bands=np.array(raw_fast_slow.band)
events_fast=np.array(raw_fast_slow.fast)
events_slow=np.array(raw_fast_slow.slow)

for i in range(len(bands)):
    band=bands[i]
    event_fast=events_fast[i]
    event_slow=events_slow[i]

    #gather photometry
    target_file_fast=os.path.join(file_dir,f'downloaded/tmp/photometry/{event_fast}.tsv')
    target_file_slow=os.path.join(file_dir,f'downloaded/tmp/photometry/{event_slow}.tsv')
    data_fast=pd.read_csv(target_file_fast,sep='\t')
    data_slow=pd.read_csv(target_file_slow,sep='\t')
    photometry_fast=data_fast.loc[data_fast['band']==band]
    photometry_slow=data_slow.loc[data_slow['band']==band]

    #put time and magnitude in different arrays
    time_fast=np.array(photometry_fast.time)
    time_slow=np.array(photometry_slow.time)
    magnitude_fast=np.array(photometry_fast.magnitude)
    magnitude_slow=np.array(photometry_slow.magnitude)

    #MJD time to relative time from the begining
    time_fast=[Time(i,format='mjd') for i in time_fast]
    T0_fast=time_fast[0]
    time_fast=[i.datetime64 for i in time_fast]
    T0_fast=T0_fast.datetime64
    time_fast=np.array([float(ti-T0_fast)/(1e9*3600*24) for ti in time_fast])#in days

    time_slow=[Time(i,format='mjd') for i in time_slow]
    T0_slow=time_slow[0]
    time_slow=[i.datetime64 for i in time_slow]
    T0_slow=T0_slow.datetime64
    time_slow=np.array([float(ti-T0_slow)/(1e9*3600*24) for ti in time_slow])#in days

    #fiting
    spl_fast=UnivariateSpline(time_fast,magnitude_fast,k=4)
    spl_slow=UnivariateSpline(time_slow,magnitude_slow,k=4)

    max_time=min(np.max(time_fast),np.max(time_slow))
    x=np.linspace(0,max_time,1000)
    fit_fast=spl_fast(x)
    fit_slow=spl_slow(x)

    plt.plot(time_fast,magnitude_fast,label='fast')
    plt.plot(x,fit_fast,'b')
    plt.plot(time_slow,magnitude_slow,label='slow')
    plt.plot(x,fit_slow,'b')
    plt.legend()
    plt.show()
