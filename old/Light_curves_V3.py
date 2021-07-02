import pandas as pd
import numpy as np
import requests as req
from astropy.time import Time
import matplotlib.pyplot as plt

##variables

dir='C:\\Users\\cleme\\Desktop\\APC_2021\\'
SN_names=pd.read_csv(dir+'SN_names.txt', sep="\n", header=None)
U,B,V,R,I,J,H,K=({'event':[],'time':[],'e_time':[],'u_time':[],'magnitude':[],'e_magnitude':[],'band':[],'upperlimit':[]} for i in range(8))

##functions

def write(object,path):
    f=open(path,'w')
    f.write(object)
    f.close()

def gather(SN_names):
    events_metadata={'event':[],'claimedtype':[],'ebv':[],'lumdist':[]}
    events_photometry={'event':[],'time':[],'e_time':[],'u_time':[],'magnitude':[],'e_magnitude':[],'band':[],'upperlimit':[]}
    for name in SN_names[0]:
        meta_request=req.get(f'https://api.sne.space/{name}?format=csv').text
        write(meta_request,dir+'meta_tmp.csv')
        meta=pd.read_csv(dir+'meta_tmp.csv')
        photometry_request=req.get(f'https://api.astrocats.space/{name}/photometry/time+e_time+u_time+magnitude+e_magnitude+band+upperlimit?format=csv').text
        write(photometry_request,dir+'photometry_tmp.csv')
        photometry=pd.read_csv(dir+'photometry_tmp.csv')
        for i in events_metadata.keys():
            events_metadata[i].append(meta[i])
        for i in events_photometry.keys():
            for j in range(len(photometry[i])):
                events_photometry[i].append(photometry[i][j])
    metadf=pd.DataFrame(events_metadata)
    photometrydf=pd.DataFrame(events_photometry)
    return(metadf,photometrydf)

def Maxtime(V):
    name=np.array(V['event'])
    time=np.array(V['time'])
    mag=np.array(V['magnitude'])
    maxtime={'event':[],'maxtime':[]}
    for event in meta['event']:
        nametmp=event.values[0]
        arg=np.where(name==nametmp)
        timetmp=time[arg]
        magtmp=mag[arg]
        if len(magtmp)>0:
            argmax=np.argmin(magtmp)#argmin parceque magnitude
            timemax=time[arg[0][0]+argmax]
            maxtime['event'].append(nametmp)
            maxtime['maxtime'].append(timemax)
        else:
            maxtime['event'].append(nametmp)
            maxtime['maxtime'].append(None)
    return pd.DataFrame(maxtime)

def time_rescale(maxVtime,band):
    name=np.array(band['event'])
    time=np.array(band['time'])
    for event in meta['event']:
        nametmp=event.values[0]
        arg=np.where(name==nametmp)
        argmaxtime=np.where(maxVtime.event==nametmp)[0]
        T0=maxVtime['maxtime'][argmaxtime].values[0]
        timetmp=time[arg]
        if len(timetmp)<1:
            continue
        T0=Time(T0,format='mjd')
        T0.format='datetime64'
        T0=T0.value
        for t in range(len(timetmp)):
            ti=timetmp[t]
            ti=Time(ti,format='mjd')
            ti.format='datetime64'
            ti=ti.value
            delta=float((ti-T0)/(1e9*3600*24))#en jours
            band['time'][arg[0][t]]=delta

def correction(band,ebv):
    cor={'U':1.569,'B':1.337,'V':1.000,'R':0.751,'I':0.479,'J':0.282,'H':0.190,'K':0.114}
    cortmp=cor[band['band'][0]]
    for event in meta['event']:
        nametmp=event.values[0]
        arg=np.where(np.array(band['event'])==nametmp)
        argevent=np.where(np.array(ebv['event'])==nametmp)[0][0]
        if len(arg[0])<1:
            continue
        for mag in range(len(arg[0])):
            band['magnitude'][arg[0][mag]]+=3.1*ebv['ebv'][argevent]*cortmp

def plot_band(event,band,strband):
    arg=np.where(np.array(band['event'])==event)
    timearray=np.array(band['time'])
    magarray=np.array(band['magnitude'])
    timetest=timearray[arg]
    magtest=magarray[arg]
    if len(magtest)<1:
        return
    plt.plot(timetest,magtest,'.',label=strband)
    plt.ylabel('magnitude absolue')
    plt.xlabel('temps en jours')

##core
meta,photo=gather(SN_names)

for i in range(len(photo)):
    if (photo['band'][i]=='U') or (photo['band'][i]=='u') or (photo['band'][i]=="U'") or (photo['band'][i]=="u'"):
        for j in photo.keys():
            U[j].append(photo[j][i])
    elif (photo['band'][i]=='B') or (photo['band'][i]=='b') or (photo['band'][i]=="B'") or (photo['band'][i]=="b'"):
        for j in photo.keys():
            B[j].append(photo[j][i])
    elif (photo['band'][i]=='V') or (photo['band'][i]=='v') or (photo['band'][i]=="V'") or (photo['band'][i]=="v'"):
        for j in photo.keys():
            V[j].append(photo[j][i])
    elif (photo['band'][i]=='R') or (photo['band'][i]=='r') or (photo['band'][i]=="R'") or (photo['band'][i]=="r'"):
        for j in photo.keys():
            R[j].append(photo[j][i])
    elif (photo['band'][i]=='I') or (photo['band'][i]=='i') or (photo['band'][i]=="I'") or (photo['band'][i]=="i'"):
        for j in photo.keys():
            I[j].append(photo[j][i])
    elif (photo['band'][i]=='J') or (photo['band'][i]=='j') or (photo['band'][i]=="J'") or (photo['band'][i]=="j'"):
        for j in photo.keys():
            J[j].append(photo[j][i])
    elif (photo['band'][i]=='H') or (photo['band'][i]=='h') or (photo['band'][i]=="H'") or (photo['band'][i]=="h'"):
        for j in photo.keys():
            H[j].append(photo[j][i])
    elif (photo['band'][i]=='K') or (photo['band'][i]=='k') or (photo['band'][i]=="K'") or (photo['band'][i]=="k'"):
        for j in photo.keys():
            K[j].append(photo[j][i])

maxVtime=Maxtime(V)
EBV={'event':[meta['event'][i].values[0] for i in range(len(meta))],'ebv':[meta['ebv'][j].values[0] for j in range(len(meta))]}
time_rescale(maxVtime,U)
time_rescale(maxVtime,B)
time_rescale(maxVtime,V)
time_rescale(maxVtime,R)
time_rescale(maxVtime,I)
time_rescale(maxVtime,J)
time_rescale(maxVtime,H)
time_rescale(maxVtime,K)
correction(U,EBV)
correction(B,EBV)
correction(V,EBV)
correction(V,EBV)
correction(R,EBV)
correction(I,EBV)
correction(J,EBV)
correction(H,EBV)
correction(K,EBV)

for event in meta['event']:
    testevent=event.values[0]

    plot_band(testevent,U,'U')
    plot_band(testevent,B,'B')
    plot_band(testevent,V,'V')
    plot_band(testevent,R,'R')
    plot_band(testevent,I,'I')
    plot_band(testevent,J,'J')
    plot_band(testevent,H,'H')
    plot_band(testevent,K,'K')

    plt.title('courbe de lumière')
    plt.legend()
    plt.gca().invert_yaxis()
    plt.show()