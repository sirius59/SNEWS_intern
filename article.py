## Import libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline,BPoly


## Functions

def read_lightcurves(path):
    time=[[]]
    mag=[[]]
    data=open(path,'r').read().split('\n')
    for i in data:
        if i=='/':
            time.append([])
            mag.append([])
        elif i=='':
            continue
        else:
            tmp=i.split('\t')
            time[-1].append(float(tmp[0]))
            mag[-1].append(float(tmp[1]))
    del(time[-1],mag[-1])
    return time,mag

def argTmax(time):
    args=np.where(np.array(time)<70)
    return args[0][-1]

def write_art(param,knots,path): #permet d'ecrire dans un document
    f=open(path,'w')
    line=''
    for i in param:
        line+=str(i)+'\t'
    line+='\n'
    for i in knots:
        line+=str(i)+'\t'
    f.write(line)
    f.close()

def meancurve(slow,fast):
    mean=[]
    for i in range(len(slow)):
        mean.append((slow[i]+fast[i])/2)
    return np.array(mean)

##core
time,mag=read_lightcurves(dirtmp+LC)

params=[]
knots=[]

for i in range(len(time)):
    cut=argTmax(time[i])
    T=time[i][:cut]
    M=mag[i][:cut]

    spl=UnivariateSpline(T,M,k=5)
    params.append([[j] for j in spl.get_coeffs()])
    knots.append(spl.get_knots())

x=np.linspace(-20,30,10000)
slow=BPoly(params[0],knots[0])
fast=BPoly(params[1],knots[1])
slowcurve=slow(x)
fastcurve=fast(x)
mean=meancurve(slowcurve,fastcurve)

plt.plot(x,slowcurve,label='slow')
plt.plot(x,fastcurve,label='fast')
plt.plot(x,mean,label='mean')
plt.gca().invert_yaxis()
plt.legend()
plt.title('bande '+bandstr)
plt.xlabel('temps en jours')
plt.ylabel('magnitude absolue')
plt.show()