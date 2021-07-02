##Libraries

import numpy as np
import requests as req
from astropy.time import Time
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



dirtmp='C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\' #chemin du directory
dir='C:\\Users\\cleme\\Desktop\\APC_2021\\'

##preprocess les données des profils slow et fast 1B/C
filename='SN1BC_article'
event=np.array(open(dirtmp+filename+'.txt','r').read().split('\n')) #list de nom des évènements

exec(open(dir+'Light_curves.py','r').read()) #execute le code Light_curves.py

##effectue un fit et la moyenne en bande U
bandstr='V'
LC=bandstr+'.txt'

exec(open(dir+'article.py','r').read()) #execute le code Light_curves.py


##preprocess les données de 89 SN1BC
filename='SN1bc'
event=np.array(open(dirtmp+filename+'.txt','r').read().split('\n')) #list de nom des évènements

exec(open(dir+'Light_curves.py','r').read()) #execute le code Light_curves.py

##définie la distribution en magnitude pour la bande donnée
exec(open(dir+'mag_histo.py','r').read())

##défini la distibution des distances
exec(open(dir+'distance_distrib.py','r').read())