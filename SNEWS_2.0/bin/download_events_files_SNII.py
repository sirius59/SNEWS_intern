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

def filter_II(df):
    index_nb=[]
    for i in df.index:
        if 'Ia' in df.claimedtype[i]: #delete Ia type
            index_nb.append(i)
        elif 'Ib' in df.claimedtype[i]: #delete type Ib
            index_nb.append(i)
        elif 'Ic' in df.claimedtype[i]: #delete type Ic
            index_nb.append(i)
        elif 'GRB' in df.claimedtype[i]: #delete GRBs
            index_nb.append(i)
        elif '?' in df.claimedtype[i]: #delete uncertain type
            index_nb.append(i)
        elif 'test' in df.event[i]: #delete test of Nikola
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

##SNII

if not os.path.isfile(os.path.join(file_dir,'downloaded/events_II.csv')): #if no file, download it
    print('Downloading catalog SN II...')
    print('The first run could take several minutes')
    URL_events='https://api.sne.space/catalog/alias+claimedtype?claimedtype=II&format=tsv' #request all type Ic
    request_tsv=req.get(URL_events).text #http request
    write_tmp('downloaded/tmp/tmp_tsv.tsv',request_tsv) #write in a temporary file

    df=pd.read_csv(os.path.join(file_dir,'downloaded/tmp/tmp_tsv.tsv'),sep='\t') #read the tsv and put it in a DataFrame

    df=filter_twins(df) #delete twin events
    df=filter_II(df) #delete uncertain type supernovae

    df['event'].to_csv(os.path.join(file_dir,'downloaded/events_II.csv'),index=False)
else:
    print('Catalog SN II: OK')