## Import libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy


maxabs=np.loadtxt(dirtmp+bandstr+'_maxabs.txt')
min=int(round(np.min(maxabs),0))
max=int(round(np.max(maxabs),0)+1)
delta=max-min
bins=np.linspace(min,max,delta+1)

test=np.digitize(maxabs,bins)

probalist,binlist,c=plt.hist(maxabs,bins=bins,density=True)
np.savetxt(dirtmp+'mag_distrib.txt',np.array([probalist,binlist[:-1]]))
plt.show()