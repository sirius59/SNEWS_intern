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

    if len(is_in)>0 and name not in event_OK:
        event_OK.append(name)
    for band in is_in:
        globals()[f'event_{band}'].append(name)


##CORE
##check directories

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
check_dir_and_create('data')#check if the directory is available and if not create it
check_dir_and_create('data/II')
requested_band=['U','G','R','I','Z','Y','J','H','K','V']
event_OK=[]


for str_band in requested_band:
    if not os.path.isfile(os.path.join(file_dir,f'data/II/events_II_{str_band}.csv')) or not os.path.isfile(os.path.join(file_dir,f'data/events_II_USED.csv')): #if no file, download it

        print('Filtering data...')
        event_name=pd.read_csv(os.path.join(file_dir,'downloaded/events_II.csv')).event

        #check if all meta data available
        event_meta_OK=[]

        for name in event_name:
            if check_meta(name):
                event_meta_OK.append(name)

        #check if photometry data is available
        event_U,event_V,event_R,event_I,event_Z,event_Y,event_J,event_H,event_K,event_G=([] for i in range(10))

        for name in event_meta_OK:
            check_photometry(name)

        #save in file
        dfU=pd.DataFrame(data=event_U)
        dfV=pd.DataFrame(data=event_V)
        dfR=pd.DataFrame(data=event_R)
        dfI=pd.DataFrame(data=event_I)
        dfZ=pd.DataFrame(data=event_Z)
        dfY=pd.DataFrame(data=event_Y)
        dfJ=pd.DataFrame(data=event_J)
        dfH=pd.DataFrame(data=event_H)
        dfK=pd.DataFrame(data=event_K)
        dfG=pd.DataFrame(data=event_G)


        dfU[0].to_csv(os.path.join(file_dir,'data/II/events_II_U.csv'),index=False,header=False)
        dfV[0].to_csv(os.path.join(file_dir,'data/II/events_II_V.csv'),index=False,header=False)
        dfR[0].to_csv(os.path.join(file_dir,'data/II/events_II_R.csv'),index=False,header=False)
        dfI[0].to_csv(os.path.join(file_dir,'data/II/events_II_I.csv'),index=False,header=False)
        dfZ[0].to_csv(os.path.join(file_dir,'data/II/events_II_Z.csv'),index=False,header=False)
        dfY[0].to_csv(os.path.join(file_dir,'data/II/events_II_Y.csv'),index=False,header=False)
        dfJ[0].to_csv(os.path.join(file_dir,'data/II/events_II_J.csv'),index=False,header=False)
        dfH[0].to_csv(os.path.join(file_dir,'data/II/events_II_H.csv'),index=False,header=False)
        dfK[0].to_csv(os.path.join(file_dir,'data/II/events_II_K.csv'),index=False,header=False)
        dfG[0].to_csv(os.path.join(file_dir,'data/II/events_II_G.csv'),index=False,header=False)

        dfOK=pd.DataFrame(data=event_OK)
        dfOK[0].to_csv(os.path.join(file_dir,'data/events_II_USED.csv'),index=False,header=False)