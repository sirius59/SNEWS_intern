## Import libraries
import numpy as np
import matplotlib.pyplot as plt

## Functions

def read_lightcurves(path):
    time=[]
    mag=[]
    data=open(path,'r').read().split('\n')
    for i in data:
        if i=='/' or i=='':
            continue
        else:
            tmp=i.split('\t')
            time.append(float(tmp[0]))
            mag.append(float(tmp[1]))
    return time,mag

def write_mean(time,mag,path): #permet d'ecrire dans un document
    f=open(path,'w')
    for i in range(len(time)):
        if np.isnan(mag[i]):
            continue
        else:
            f.write(str(time[i])+'\t'+str(mag[i])+'\n')
    f.close()

##core
time,mag=read_lightcurves(dirtmp+LC)

tmin,tmax,dt=round(min(time),0),int(max(time)),0.5
timebins=np.array([round(tmin+i*dt,1) for i in range(int(1/dt*(tmax-tmin)+1))])
magbins=[[] for i in range(len(timebins))]
meanmag=[]

for i in range(len(time)):
    argument=np.where(abs(timebins-time[i])<0.5)
    if len(argument[0])==0:
        continue
    else:
        intargument=int(argument[0][0])
        magbins[intargument].append(mag[i])

for i in magbins:
    if len(i)>7:
        meanmag.append(np.mean(i))
    else:
        meanmag.append(np.nan)

write_mean(timebins,meanmag,dirtmp+band+'_mean.txt')

plt.plot(timebins,meanmag,'.',label=band+' mean')
plt.gca().invert_yaxis()
#plt.title('3e test de moyenne sur l\'échantillon de SN')
plt.xlabel('temps en jours')
plt.ylabel('magnitude absolue')
plt.legend()
plt.show()