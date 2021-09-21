##Libraries

import os
import requests as req
import pandas as pd
import numpy as np

##Functions

def check_dir_and_create(target):
    target_dir=os.path.join(file_dir,target) #path of the targeted dir

    if not os.path.isdir(target_dir): #if no dir, create it
        os.mkdir(target_dir)

def band_data(photometry,bande): #return all the photometry associated with the wanted band
    band_photometry=photometry.loc[(photometry['band']==bande)]
    return band_photometry

def check_enouh_data(data,eps=10): #check if the len of band_data > eps
    if len(data)>eps:
        return True
    else:
        return False

##CORE
##check directories

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
dir_photometry=os.path.join(file_dir,"downloaded/tmp/photometry")
dir_events=os.path.join(file_dir,'data/IBC')
requested_band=['U','G','R','I','Y','J','H','V']
check_dir_and_create('data/max_mag')
event_USED=[]
to_write={'event':[],'claimedtype':[],'ebv':[],'lumdist':[]}


if not os.path.isfile(os.path.join(file_dir,f'data/events_USED.txt')): #if no file, download it
    print('checking data...')
    for band in requested_band: #for each band
        photometry_OK=[]
        target_file_event=os.path.join(dir_events,f'events_IBC_{band}.csv')
        names=pd.read_csv(target_file_event,header=None)[0]
        for event in names: #for each event
            target_file_photometry=os.path.join(dir_photometry,f'{event}.tsv')
            photometry_tmp=pd.read_csv(target_file_photometry,sep='\t')
            band_photometry=band_data(photometry_tmp,band) #get the photometry associated with the band
            if check_enouh_data(band_photometry): # if not enough data (<10 points)
                photometry_OK.append(event)
            else:
                continue
        if len(photometry_OK)>=10: #if enough events
            globals()[f'event_{band}']=photometry_OK
            globals()[f'df{band}']=pd.DataFrame(data=globals()[f'event_{band}'])
            globals()[f'df{band}'][0].to_csv(os.path.join(file_dir,f'data/IBC/events_IBC_{band}.csv'),index=False,header=False)
            for i in photometry_OK: #append all the events used in this programm in event_USED
                if i not in event_USED:
                    event_USED.append(i)
        else:
            globals()[f'event_{band}']=[np.nan]
            globals()[f'df{band}']=pd.DataFrame(data=globals()[f'event_{band}'])
            globals()[f'df{band}'][0].to_csv(os.path.join(file_dir,f'data/IBC/events_IBC_{band}.csv'),index=False,header=False)
    for i in event_USED: #write in the file event_USED.txt all the meta data of the events used (for the table of the report)
        target_file=os.path.join(dir_photometry,f'../meta/{i}.tsv')
        meta_tmp=pd.read_csv(target_file,sep='\t')
        to_write['event'].append(meta_tmp.event.values[0])
        to_write['claimedtype'].append(meta_tmp.claimedtype.values[0])
        to_write['ebv'].append(meta_tmp.ebv.values[0])
        to_write['lumdist'].append(meta_tmp.lumdist.values[0])
    dftw=pd.DataFrame(data=to_write)
    dftw.to_csv(os.path.join(file_dir,f'data/events_USED.txt'),index=False,header=False)