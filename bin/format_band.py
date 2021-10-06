##Libraries

import os
import requests as req
import pandas as pd
import numpy as np

##core
file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
dir_photometry=os.path.join(file_dir,"downloaded/tmp/photometry")
dir_events=os.path.join(file_dir,'data/IBC')

requested_band=['U','G','R','I','Y','J','H','V']

for band in requested_band:
    target_file_event=os.path.join(dir_events,f'events_IBC_{band}.csv')
    names=pd.read_csv(target_file_event,header=None)[0]
    for event in names: #for each event
        target_file_photometry=os.path.join(dir_photometry,f'{event}.tsv')
        photometry_tmp=pd.read_csv(target_file_photometry,sep='\t')
        event=np.array(photometry_tmp.event)
        time=np.array(photometry_tmp.time)
        magnitude=np.array(photometry_tmp.magnitude)
        band=np.array(photometry_tmp.band)
        upperlimit=np.array(photometry_tmp.upperlimit)
        band=np.array([str(i).upper() for i in band])
        tmpdf=pd.DataFrame(data={'event':event,'time':time,'magnitude':magnitude,'band':band,'upperlimit':upperlimit})
        tmpdf.to_csv(target_file_photometry,index=False,header=True,sep='\t')