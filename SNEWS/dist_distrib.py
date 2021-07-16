##Libraries

import numpy as np
from scipy.stats import rv_discrete
import matplotlib.pyplot as plt

##Directories

dirdata='C:\\Users\\cleme\\Desktop\\SNEWS\\data\\'

##Core

data=np.loadtxt(dirdata+'distance_distrib.txt',delimiter=';')
dist=data[:,0]*1e3 #distances en kPc convertie en Pc
proba=np.abs(data[:,1])

normproba=proba/np.sum(proba)

dist_distrib=rv_discrete(name='cstm',values=(dist,normproba))
plt.plot(dist,normproba)
plt.xlabel('distance en Pc')
plt.ylabel('probabilité de détection')
plt.title('distribution théoriques des supernovae dans la voie lactée')
plt.show()