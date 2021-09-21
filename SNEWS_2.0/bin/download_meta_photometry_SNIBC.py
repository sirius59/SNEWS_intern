##Libraries

import os
import requests as req
import pandas as pd

##Functions

def check_dir_and_create(target):
    target_dir=os.path.join(file_dir,target) #path of the targeted dir

    if not os.path.isdir(target_dir): #if no dir, create it
        os.mkdir(target_dir)

def check_meta_and_download(name):
    target_file=f'downloaded/tmp/meta/{name}.tsv'
    target_file=os.path.join(file_dir,target_file) #path of the targeted file

    if not os.path.isfile(target_file): #if no file, download it
        URL_events=f'https://api.sne.space/{name}/claimedtype+ebv+lumdist?format=tsv' #request all type Ib
        request_tsv=req.get(URL_events).text #http request
        write_tmp(target_file,request_tsv) #write in a temporary file

def check_photo_and_download(name):
    target_file=f'downloaded/tmp/photometry/{name}.tsv'
    target_file=os.path.join(file_dir,target_file) #path of the targeted file

    if not os.path.isfile(target_file): #if no file, download it
        URL_events=f'https://api.astrocats.space/{name}/photometry/time+magnitude+band+upperlimit?format=tsv' #request all type Ib
        request_tsv=req.get(URL_events).text #http request
        write_tmp(target_file,request_tsv) #write in a temporary file

def write_tmp(target_file,data):
    target=os.path.join(file_dir,target_file) #path of the targeted dir
    file=open(target,'w+')
    file.write(data)
    file.close()

##CORE
##check directories

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file

#check if the directory is available and if not create it
check_dir_and_create('downloaded/tmp/meta')
check_dir_and_create('downloaded/tmp/photometry')

##type IB/C
print('loading SN Ib/c meta and photometric data')

event_name=pd.read_csv(os.path.join(file_dir,'downloaded/events_IBC.csv')).event

for name in event_name:
    check_meta_and_download(name)
    check_photo_and_download(name)