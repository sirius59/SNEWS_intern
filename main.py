##Libraries

import numpy as np
import requests as req
from astropy.time import Time
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

dirtmp='C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\' #chemin du directory
dir='C:\\Users\\cleme\\Desktop\\APC_2021\\'
filename='SN1BC_article'
event=np.array(open(dirtmp+filename+'.txt','r').read().split('\n')) #list de nom des évènements

exec(open(dir+'Light_curves.py','r').read()) #execute le code Light_curves.py

band='U'
LC=band+'.txt'

exec(open(dir+'article.py','r').read()) #execute le code Light_curves.py