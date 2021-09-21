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

def check_meta(name):
    target_file=f'downloaded/tmp/meta/{name}.tsv'
    target_file=os.path.join(file_dir,target_file) #path of the targeted file

    df=pd.read_csv(target_file, sep='\t')
    ebv=df.ebv.values
    lumdist=df.lumdist.values

    if not np.isnan(ebv) and not np.isnan(lumdist):
        return True
    else:
        return False

def check_photometry(name):
    target_file=f'downloaded/tmp/photometry/{name}.tsv'
    target_file=os.path.join(file_dir,target_file) #path of the targeted file

    df=pd.read_csv(target_file, sep='\t')
    band=[i for i in df.band.values]
    is_in=[]

    if len(band)>3: # "enough" data
        #band string preprocessing
        band=[string.upper() for string in band if type(string)==type('')] #set to upper string (WARNING LIST OF NAN -> [])
        if len(band)>0:
            band=[string.replace("'",'') for string in band] #we want band of single letter without "'"
            for string in band:
                if string not in is_in and string in requested_band:
                    is_in.append(string)
                else:
                    continue
    for band in is_in:
        globals()[f'event_{band}'].append(name)


##CORE
##check directories

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
check_dir_and_create('data')#check if the directory is available and if not create it
check_dir_and_create('data/IBC')
requested_band=['U','G','R','I','Y','J','H','V']


for str_band in requested_band:
    if not os.path.isfile(os.path.join(file_dir,f'data/IBC/events_IBC_{str_band}.csv')): #if no file, download it

        print('Filtering data...')
        event_name=pd.read_csv(os.path.join(file_dir,'downloaded/events_IBC.csv')).event

        #check if all meta data available
        event_meta_OK=[]

        for name in event_name:
            if check_meta(name):
                event_meta_OK.append(name)

        #check if photometry data is available
        event_U,event_V,event_R,event_I,event_Y,event_J,event_H,event_G=([] for i in range(8))

        for name in event_meta_OK:
            check_photometry(name)

        #save in file
        dfU=pd.DataFrame(data=event_U)
        dfV=pd.DataFrame(data=event_V)
        dfR=pd.DataFrame(data=event_R)
        dfI=pd.DataFrame(data=event_I)
        dfY=pd.DataFrame(data=event_Y)
        dfJ=pd.DataFrame(data=event_J)
        dfH=pd.DataFrame(data=event_H)
        dfG=pd.DataFrame(data=event_G)


        dfU[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_U.csv'),index=False,header=False)
        dfV[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_V.csv'),index=False,header=False)
        dfR[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_R.csv'),index=False,header=False)
        dfI[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_I.csv'),index=False,header=False)
        dfY[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_Y.csv'),index=False,header=False)
        dfJ[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_J.csv'),index=False,header=False)
        dfH[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_H.csv'),index=False,header=False)
        dfG[0].to_csv(os.path.join(file_dir,'data/IBC/events_IBC_G.csv'),index=False,header=False)