##Libraries

import os
import requests as req
import pandas as pd

##Functions

def check_dir_and_create(target):
    target_dir=os.path.join(file_dir,target) #path of the targeted dir

    if not os.path.isdir(target_dir): #if no dir, create it
        os.mkdir(target_dir)

def write_tmp(target_file,data):
    target=os.path.join(file_dir,target_file) #path of the targeted dir
    file=open(target,'w+')
    file.write(data)
    file.close()

def filter_twins(df):
    index_nb=[]
    for i in df.index:
        for j in df.index:
            if i==j:
                continue
            elif df.event[i] in df.alias[j]:
                index_nb.append(max(i,j))
            else:
                continue
    return df.drop(labels=index_nb)

def filter_IBC(df):
    index_nb=[]
    for i in df.index:
        if 'Ia' in df.claimedtype[i]: #delete Ia type
            index_nb.append(i)
        elif 'II' in df.claimedtype[i]: #delete type II
            index_nb.append(i)
        elif 'GRB' in df.claimedtype[i]: #delete GRBs
            index_nb.append(i)
        elif '?' in df.claimedtype[i]: #delete uncertain type
            index_nb.append(i)
        else:
            continue
    return df.drop(labels=index_nb)

##CORE
##check directories

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file

check_dir_and_create('downloaded')#check if the directory is available and if not create it
check_dir_and_create('downloaded/tmp')

print('data checking...')

##SNIB/C

if not os.path.isfile(os.path.join(file_dir,'downloaded/events_IBC.csv')): #if no file, download it
    print('Downloading catalog SN Ib/c...')
    print('The first run could take several minutes')
    URL_events='https://api.sne.space/catalog/alias+claimedtype?claimedtype=Ib&format=tsv' #request all type Ib
    request_tsv=req.get(URL_events).text #http request
    write_tmp('downloaded/tmp/tmp_tsv.tsv',request_tsv) #write in a temporary file

    dfIb=pd.read_csv(os.path.join(file_dir,'downloaded/tmp/tmp_tsv.tsv'),sep='\t') #read the tsv and put it in a DataFrame


    URL_events='https://api.sne.space/catalog/alias+claimedtype?claimedtype=Ic&format=tsv' #request all type Ic
    request_tsv=req.get(URL_events).text #http request
    write_tmp('downloaded/tmp/tmp_tsv.tsv',request_tsv) #write in a temporary file

    dfIc=pd.read_csv(os.path.join(file_dir,'downloaded/tmp/tmp_tsv.tsv'),sep='\t') #read the tsv and put it in a DataFrame

    dict_to_df={'event':[i for i in dfIb.event]+[i for i in dfIc.event] ,'alias':[i for i in dfIb.alias]+[i for i in dfIc.alias] ,'claimedtype':[i for i in dfIb.claimedtype]+[i for i in dfIc.claimedtype]}
    df=pd.DataFrame(data=dict_to_df)


    df=filter_twins(df) #delete twin events
    df=filter_IBC(df) #delete uncertain type supernovae

    df['event'].to_csv(os.path.join(file_dir,'downloaded/events_IBC.csv'),index=False)
else:
    print('Catalog SN Ib/c: OK')