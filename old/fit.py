##import libraries
from scipy.optimize import curve_fit

def read_mean_lightcurves(path):
    time=[]
    mag=[]
    data=open(path,'r').read().split('\n')
    for i in data:
        if i=='':
            continue
        else:
            tmp=i.split('\t')
            time.append(float(tmp[0]))
            mag.append(float(tmp[1]))
    return time,mag

def f(x,a,b,c,d,x0):
    return a*(x-x0)**b*np.exp(-c*(x-x0))+d

timebins,meanmag=read_mean_lightcurves(dirtmp+band+'_mean.txt')
y=[f(i,-1/30,2,0.08,3,-25) for i in timebins]

plt.plot(timebins,meanmag, '.')
plt.plot(timebins,y)
plt.gca().invert_yaxis()
plt.show()