## Import libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline,BPoly

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
    if len(i)>3:
        meanmag.append(np.mean(i))
    else:
        meanmag.append(np.nan)

arg=np.isnan(np.array(meanmag))
arg=arg==False

T=np.array(timebins)[arg]
M=np.array(meanmag)[arg]

spl=UnivariateSpline(T,M,k=5)

x=np.linspace(-20,30,10000)
y=spl(x)

plt.plot(timebins,meanmag,'.')
plt.plot(x,y)
plt.legend()
plt.gca().invert_yaxis()
plt.show()