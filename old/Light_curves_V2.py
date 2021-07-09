##libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests as req
from scipy.optimize import curve_fit
from astropy.time import Time,TimeDelta, TimePlotDate

##Variables
type=['Ib','Ic','II']
Events=[]# [[name,'lumdist',type,'ebv'],[name,'lumdist',type,'ebv'],...] WARNING type(lumdist)=string (ie: metadata of the event)
photometry=[]# list of arrays[[arrays[time,mag,e_mag],band],[arrays[time,mag,e_mag],band],...] (ie: data relative to the raw photometry)
Events_bands=[]#magabs(band_photometry(photometry)) (ie: data relative to the absolute photometry sorted by bands)
##function
def meta_preprocess(req):# return array of ['name', 'lumdist', 'type','ebv'] from tsv file WARNING type(lumdist)=string
    reqlines=req.split('\n')[1:]
    event=[]
    for i in reqlines:
        tmp=i.split('\t')
        if ('Ia' in tmp[2]) or ('?' in tmp[2]) or ('removed' in tmp[2]) or ('galaxy' in tmp[2]):#filter the event 'removed', uncertain and multiple classification with Ia
            continue
        else:
            event.append([tmp[0],tmp[1],tmp[2],tmp[3]])
    return np.array(event)

def data_preprocess(req): #return arrays[[arrays[time,mag,e_mag],band],[arrays[time,mag,e_mag],band],...]
    reqlines=req.split('\n')[1:]
    data=[]
    for i in reqlines:
        tmp=i.split('\t')[1:]
        if tmp[2]=='':#if no error append False
            data.append([np.array([float(tmp[0]),float(tmp[1]),False]),tmp[3].upper()])
        else:
            data.append([np.array([float(tmp[0]),float(tmp[1]),float(tmp[2])]),tmp[3].upper()])
    return np.array(data)

def band_photometry(photometry_item):#return list of [[bands],array[[time],[mag],[e_mag]],[bands],array[[time],[mag],[e_mag]],...]
    photometry_item=time_rescale(photometry_item)#time rescale

    strband=[]#append all bands used
    for i in photometry_item[:,1]:
        if i not in strband:
            strband.append(i)

    output=[]
    for i in strband:
        arrayshape=photometry_item[:,0][np.where(photometry_item[:,1]==i)]
        ravelshape=np.ravel([list(k) for k in arrayshape],order='F')
        listshape=ravelshape.reshape(3,len(arrayshape))
        output.append([i,listshape])
    return(output)

def correction(band,ebv):
    cor={'U':1.569,'B':1.337,'V':1.000,'R':0.751,'I':0.479,'J':0.282,'H':0.190,'K':0.114,'L':0.056}
    for b in band:
        if b[0] in cor.keys():
            b[1][1]+=3.1*ebv*cor[b[0]]
        else:
            continue
    return band

def magabs(band,dlum,ebv):#return the same shape of the input, but the magnitude is now absolute and corrected. ATTENTION rajouter les incertitudes
    band=correction(band,ebv)
    for b in band:
        b[1][1]+=-5*(np.log10(dlum*1e6)-1)#dlum en Mpc
    return band

def time_rescale(photometry_item):
    min=Time(photometry_item[0][0][0],format='mjd')
    min.format='datetime64'
    min=min.value
    for i in photometry_item:
        ti=Time(i[0][0],format='mjd')
        ti.format='datetime64'
        ti=ti.value
        i[0][0]=float((ti-min)/(1e9*3600*24))#en jours
    return(photometry_item)


def random_plot(Events_bands): #plot a random event
    r=np.random.randint(len(Events_bands)) #choose a random event
    plot_event=Events_bands[r]#data by bands
    for band in plot_event:
        if False not in band[1][2]:#if false in error
            plt.errorbar(band[1][0],band[1][1],yerr=band[1][2],fmt='.',label=band[0])
        else:
            plt.plot(band[1][0],band[1][1],'+',label=band[0])
    plt.ylabel('absolute magnitude')
    plt.xlabel('time (jours)')
    plt.title(f'{Events[r][0]}, type: {Events[r][2]}')
    plt.legend()
    plt.gca().invert_yaxis()

def f(x,a,b,c):
    return (x-b)**a+c

def g(x,a,b,c):
    return a*x**2+b*x+c

##gathering of name, luminosity distance, time, magnitude, error magnitude, bands
for t in type:
    raw_meta=req.get(f'https://api.astrocats.space/catalog/lumdist+claimedtype+ebv?ebv&lumdist&claimedtype={t}&format=tsv').text
    meta=meta_preprocess(raw_meta)
    for i in meta:
        raw_data=req.get(f'https://api.astrocats.space/{i[0]}/photometry/time+magnitude+e_magnitude+band?time&magnitude&e_magnitude&band&format=tsv').text
        if 'Internal Server Error' in raw_data:
            continue
        data=data_preprocess(raw_data)
        if len(data)<10:#ignore events with not enough data
            continue
        elif np.isin(i[0],Events)==True:#avoid double event
            continue
        else:#append the event
            print(i)
            Events.append(i)
            photometry.append(data)

for e in range(len(Events)):
    Events_bands.append(magabs(band_photometry(photometry[e]),float(Events[e][1]),float(Events[e][3])))


##assemble
#to print all the denomination of the bands
#tmp=[]
#for e in range(len(Events_bands)):
    #for b in Events_bands[e]:
        #if b[0] not in tmp:
            #tmp.append(b[0])
        #else:
            #continue
#print(tmp)


V, G, B, M2, U, W1, W2, UVM2, UVW1, UVW2, I, Z, Y, R, J, H, K, I1, I2, W, RC, IC, T=([] for i in range(23))
time=[]

for e in range(len(Events_bands)):
    for b in Events_bands[e]:
        if b[0]=='V':
            time.append(b[1][0])
            V.append(b[1][1])
        else:
            continue

a,b,c=([] for i in range(3))

for i in range(len(time)):
    if len(time[i])<3:
        continue
    else:
        popt,pcov=curve_fit(g,time[i],V[i])
        a.append(popt[0])
        b.append(popt[1])
        c.append(popt[2])

meanA=np.mean(a)
meanB=np.mean(b)
meanC=np.mean(c)

t=[30*i/999 for i in range(1000)]
sol=[g(x,a[0],b[0],c[0]) for x in t]

plt.plot(t,sol)
plt.gca().invert_yaxis()
plt.show()


##plot

plt.subplot(221)
random_plot(Events_bands)
plt.subplot(222)
random_plot(Events_bands)
plt.subplot(223)
random_plot(Events_bands)
plt.subplot(224)
random_plot(Events_bands)

plt.show()