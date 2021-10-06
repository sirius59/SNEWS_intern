##Libraries

import os
import requests as req
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rv_discrete

##Core

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
file_distance=os.path.join(file_dir,'data/distance_distrib.txt')
save_distance=os.path.join(file_dir,'graph/distance_distribution.pdf')

data_distance=np.loadtxt(file_distance,delimiter=';')
distance=data_distance[:,0]*1e3 #distance in pc
proba=data_distance[:,1] #some points near 0 are negatives --> translate a bit
proba=proba+np.abs(np.min(proba))

normproba=proba/np.sum(proba)

distance_distribution=rv_discrete(name='distance',values=(distance,normproba))

plt.plot(distance*1e-3,normproba)
plt.title('Distance distribution of SNe from the Sun',fontsize=17)
plt.xlabel('Distance in kpc',fontsize=15)
plt.ylabel('normalized probability',fontsize=15)
plt.savefig(save_distance, dpi=150, bbox_inches='tight')