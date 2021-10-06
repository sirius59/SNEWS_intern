##Libraries

import os
import requests as req
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rv_discrete

##Function

def latitude_function(z):
    H=15 #30° caracteristic thickness of the galactic disk
    return np.exp(-np.abs(z)/H)

##Core

requested_band=['U','G','R','I','Y','J','H','V']
file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
file_distance=os.path.join(file_dir,'data/distance_distrib.txt')

#distance distribution
data_distance=np.loadtxt(file_distance,delimiter=';')
distance=data_distance[:,0]*1e3 #distance in pc
proba=data_distance[:,1] #some points near 0 are negatives --> translate a bit
proba=proba+np.abs(np.min(proba))

normproba=proba/np.sum(proba)

distance_distribution=rv_discrete(name='distance',values=(distance,normproba))

#latitude distribution
latitude=np.linspace(-90,90,1000)
proba_latitude=latitude_function(latitude)
norm_proba_lat=proba_latitude/np.sum(proba_latitude)
latitude_distribution=rv_discrete(name='latitude',values=(latitude,norm_proba_lat))

#MONTECARLO
N=10

for band in requested_band:

    #make the distribution for a given photometric band
    target_file=os.path.join(file_dir,f'data/max_mag/max_mag_IBC_{band}.txt')
    data_max_mag=pd.read_csv(target_file,header=None)[0]

    min=int(round(np.min(data_max_mag),0))
    max=int(round(np.max(data_max_mag),0)+1)
    delta=max-min
    bins=np.linspace(min,max,delta+1)

    probalist,binlist,c=plt.hist(data_max_mag,bins=bins,density=True,histtype='step')
    absolute_magnitude_distribution=rv_discrete(name=f'absmag_{band}',values=(binlist[:-1],probalist))
    plt.clf()#clear the canvas for a latter plot

    MC_absolute_magnitude=absolute_magnitude_distribution.rvs(size=N)
    MC_latitude=latitude_distribution.rvs(size=N)
    MC_longitude=np.random.uniform(0,360,size=N)
    MC_distance=distance_distribution.rvs(size=N)
