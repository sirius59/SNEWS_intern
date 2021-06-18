##Libraries

import numpy as np
import requests as req
from astropy.time import Time
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

dirtmp='C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\' #chemin du directory
dir='C:\\Users\\cleme\\Desktop\\APC_2021\\'
filename='SN1BC_names'
event=np.array(open(dirtmp+filename+'.txt','r').read().split('\n')) #list de nom des évènements

exec(open(dir+'Light_curves.py','r').read()) #execute le code Light_curves.py

band='V'
LC=band+'.txt'

exec(open(dir+'moy.py','r').read()) #execute le code moy.py