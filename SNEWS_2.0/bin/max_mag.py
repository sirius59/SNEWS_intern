##Libraries

import os
import requests as req
import pandas as pd
import numpy as np

##Function

def band_magnitude(event,band): #return the magnitude associated with the band
    target_file=os.path.join(file_dir,f'downloaded/tmp/photometry/{event}.tsv')
    photometry=pd.read_csv(target_file,sep='\t')
    band_photometry=photometry.loc[(photometry['band']==band)]
    magnitude=[i for i in band_photometry.magnitude]
    return magnitude

def dust_suppressor(event,max_mag,band): #eliminate the dust extinction
    target_file=os.path.join(file_dir,f'downloaded/tmp/meta/{event}.tsv')
    ebv=float(pd.read_csv(target_file,sep='\t').ebv)
    correction_dictionary={'U':1.557,'B':1.306,'G':1.238,'V':0.997,'R':0.815,'I':0.589,'Y':0.391,'J':0.293,'H':0.184}
    kappa=correction_dictionary[band]
    max_mag+=-3.1*ebv*kappa
    return(max_mag)

def app_to_abs(event,max_mag): #apparent magnitude to absolute magnitude
    target_file=os.path.join(file_dir,f'downloaded/tmp/meta/{event}.tsv')
    lumdist=float(pd.read_csv(target_file,sep='\t').lumdist)
    max_mag+=-5*(np.log10(lumdist*1e6)-1)
    return(max_mag)

##CORE

requested_band=['U','G','R','I','Y','J','H','V']
file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
event_dir=os.path.join(file_dir,'data/IBC')

for band in requested_band: #for each band
    if not os.path.isfile(os.path.join(file_dir,f'data/max_mag/max_mag_IBC_{band}.txt')): #if no file, download it
        target_file=os.path.join(event_dir,f'events_IBC_{band}.csv')
        band_events=pd.read_csv(target_file,header=None)[0]# contain all events with this band in the photometry
        maximum_mag_band=[]
        for event in band_events:#for each event
            max_magnitude=np.min(band_magnitude(event,band))# get the maximum magnitude (min because reversed axis)
            max_magnitude=dust_suppressor(event,max_magnitude,band)# eliminate the dust extinction
            max_magnitude=app_to_abs(event,max_magnitude) #apparent to absolute magnitude
            maximum_mag_band.append(max_magnitude)
        new_target_file=os.path.join(file_dir,f'data/max_mag/max_mag_IBC_{band}.txt')
        dfmaxmag=pd.DataFrame(data=maximum_mag_band)
        dfmaxmag.to_csv(new_target_file,index=False,header=False) #write the maximum magnitude in a file for each band