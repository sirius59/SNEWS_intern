##Libraries

import numpy as np
import requests as req
from astropy.time import Time
import matplotlib.pyplot as plt
import scipy
from scipy.stats import rv_discrete,ks_2samp
from scipy.interpolate import UnivariateSpline,BPoly
from astropy.coordinates import SkyCoord
import astropy

##Variables

dirtmp='C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\' #chemin du directory des fichiers temporaires
dirdata='C:\\Users\\cleme\\Desktop\\APC_2021\\data\\'
dir='C:\\Users\\cleme\\Desktop\\APC_2021\\'

##Objects

class Band: #classe band qui permettra de manipuler les données par bandes

    def __init__(self,name):#procédure d'initialisation

        #On récupères toutes les données qui correspondent a la bande demandée
        timetmp=[]
        e_timetmp=[]
        u_timetmp=[]
        magtmp=[]
        e_magtmp=[]
        bandtmp=[]
        for i in range(len(band)):
            eventargument=np.where(np.array(band[i])==name.upper())
            timetmp.append(np.array(time[i])[eventargument])
            e_timetmp.append(np.array(e_time[i])[eventargument])
            u_timetmp.append(np.array(u_time[i])[eventargument])
            magtmp.append(np.array(magnitude[i])[eventargument])
            e_magtmp.append(np.array(e_magnitude[i])[eventargument])

        self.Name=name #string de la bande (ie 'U')
        self.Time=timetmp # tableau des temps (ie [[temps event1],[temps event2]...] )
        self.E_time=e_timetmp #pareil mais pour les erreurs sur le temps
        self.U_time=u_timetmp #pareil mais pour les unité du temps
        self.Magnitude=magtmp #pareil mais avec les magnitudes (ie [[magnitudes event1],[magnitudes event2]...] )
        self.E_magnitude=e_magtmp #pareil mais pour les erreurs de magnitudes
        self.Event=event #liste des noms des évènements (ie ['SN2002ap','SN2011dh',...] )
        self.Type=type #pareil mais avec le type associé
        self.EBV=ebv #pareil mais avec le E(B-V) associés
        self.Lumdist=lumdist #pareil mais avec la distance luminosité associée
        self.Maxabs=[]#initialisation pour ajouter le maximum de labande plus tard

    def time_rescale(self,Tmax): #replace le temps t=0 au niveau du pic en bande V
        for i in range(len(Tmax)):
            T0=Time(Tmax[i], format='mjd') #temps correspondant au pic en bande V au format MJD
            T0.format='datetime64'
            T0=T0.value #on récupère T0 au format datetime64
            for j in range(len(self.Time[i])):
                ti=self.Time[i][j]
                ti=Time(ti, format='mjd')
                ti.format='datetime64'
                ti=ti.value #valeur de chaque temps au format datetime64
                deltaT=float((ti-T0))/(1e9*3600*24)#en jours
                self.Time[i][j]=deltaT #on remplace chaque temps par le delta en jour par rapport au pic en bande V

    def mag_abs(self): #ATTENTION à executer toujours après la correction en couleur
        for i in range(len(self.Magnitude)):
            d=self.Lumdist[i]*1e6 #distance luminosité en Pc
            for j in range(len(self.Magnitude[i])):
                self.Magnitude[i][j]+=-5*(np.log10(d)-1)#passe les valeurs de magnitudes en magnitude absolue

    def correction(self):
        correction_dictionary={'U':1.569,'B':1.337,'V':1.000,'R':0.751,'I':0.479,'J':0.282,'H':0.190,'K':0.114} #dictionnaire des coefficients de correction
        correct_coef=correction_dictionary[self.Name] #selectionne la valeur de correction
        for i in range(len(self.Magnitude)):
            Ebv=self.EBV[i] # valeur de E(B-V) correspondante à l'event
            for j in range(len(self.Magnitude[i])):
                self.Magnitude[i][j]+=-3.1*Ebv*correct_coef #corrige l'excès de couleur

    def mag_rescale(self): #ATTENTION à executer après le passage aux magnitudes absolues
        for i in range(len(self.Magnitude)):
            mag=self.Magnitude[i] #liste des magnitudes
            if len(mag)<1: #si la liste est vide ne fais rien
                continue
            else:
                magabs_max=np.min(mag) #maximum en magnitude (np.min car magnitude)
                self.Maxabs.append(magabs_max)
            for j in range(len(mag)):
                self.Magnitude[i][j]+=-magabs_max #on passe ne magnitude absolue


##Functions

def write(object,path): #permet d'ecrire dans un document
    f=open(path,'w')
    f.write(object)
    f.close()

def read_meta(path): #permet de lire correctement le fichier des metadonnées
    data=open(path,'r').readlines()
    return data[1].split('\t')

def read_photometry(path): #permet de lire correctement le fichier des données photometriques
    data=open(path,'r').read().split('\n')
    return data[1:]

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

def gather(SN_names): #permet de collecter toutes les données depuis l'API
    type=[]
    ebv=[]
    lumdist=[]
    time=[]
    e_time=[]
    u_time=[]
    magnitude=[]
    e_magnitude=[]
    bande=[]
    for name in SN_names:

        metadata_request=req.get(f'https://api.sne.space/{name}?format=tsv').text
        write(metadata_request,dirtmp+'meta_tmp.txt')
        metadata=read_meta(dirtmp+'meta_tmp.txt')

        type.append(metadata[3])
        ebv.append(float(metadata[8]))
        lumdist.append(float(metadata[15]))

        photometry_request=req.get(f'https://api.astrocats.space/{name}/photometry/time+e_time+u_time+magnitude+e_magnitude+band+upperlimit?format=tsv').text
        write(photometry_request,dirtmp+'photometry_tmp.txt')
        photometry=read_photometry(dirtmp+'photometry_tmp.txt')

        timetmp=[] #liste des temps
        e_timetmp=[] #etc..
        u_timetmp=[]
        magtmp=[]
        e_magtmp=[]
        bandtmp=[]
        for i in range(len(photometry)):
            phototmp=photometry[i].split('\t')
            upperlimit=phototmp[-1]
            if upperlimit=='T' or phototmp[4]=='':#ignore les upper limits ou lorsque la magnitude est vide
                continue
            elif (phototmp[2]=='' or phototmp[5]=='') and "'" in phototmp[6]: #adaptation du code si pas de valeur pour les erreurs and retire les ' des bande (ie r' -> R)
                timetmp.append(float(phototmp[1]))
                e_timetmp.append(phototmp[2]) #ajoute ''
                u_timetmp.append(phototmp[3])
                magtmp.append(float(phototmp[4]))
                e_magtmp.append(phototmp[5]) #ajoute ''
                bandtmp.append(phototmp[6].upper()[:-1]) #transforme r' en R
            elif phototmp[2]=='' or phototmp[5]=='': #adaptation du code si pas de valeur pour les erreurs and retire les ' des bande (ie r' -> R)
                timetmp.append(float(phototmp[1]))
                e_timetmp.append(phototmp[2]) #ajoute ''
                u_timetmp.append(phototmp[3])
                magtmp.append(float(phototmp[4]))
                e_magtmp.append(phototmp[5]) #ajoute ''
                bandtmp.append(phototmp[6].upper()) #transforme r en R
            else:
                timetmp.append(float(phototmp[1]))
                e_timetmp.append(float(phototmp[2])) #transforme en float
                u_timetmp.append(phototmp[3])
                magtmp.append(float(phototmp[4]))
                e_magtmp.append(float(phototmp[5])) #transforme en float
                bandtmp.append(phototmp[6].upper()) #transforme r en R

        time.append(timetmp)
        e_time.append(e_timetmp)
        u_time.append(u_timetmp)
        magnitude.append(magtmp)
        e_magnitude.append(e_magtmp)
        bande.append(bandtmp)
    return(np.array(type),np.array(ebv),np.array(lumdist),np.array(time),np.array(e_time),np.array(u_time),np.array(magnitude),np.array(e_magnitude),np.array(bande))

def maxVtime():#recherche le temps au pic en bande V
    maxtime=[]
    for i in range(len(V.Magnitude)):
        mag=V.Magnitude[i]
        Ti=V.Time[i]
        if len(mag)<5:
            print(event[i])
            continue
        else:
            max_argument=np.argmin(mag)#min car magnitude
            maxtime.append(Ti[max_argument])
    return maxtime #retourne la list des temps maximaux

def argTmax(time):
    args=np.where(np.array(time)<70)
    return args[0][-1]

def meancurve(slow,fast):
    mean=[]
    for i in range(len(slow)):
        mean.append((slow[i]+fast[i])/2)
    return np.array(mean)

def relativ_magabs(t):
    mu=moyenne(t)
    sigma=abs(fast(t)-slow(t))/6
    return np.random.normal(mu,sigma)

def curve(t,random_abs):
    ratio=(moyenne(t)-random_abs)/(moyenne(t)-slow(t))
    time=np.linspace(t,30,1000)
    lightcurve=[random_abs]
    for temps in time[1:]:
        lightcurve.append(moyenne(temps)-ratio*(moyenne(temps)-slow(temps)))
    return(time,np.array(lightcurve))

def abs_to_app(M,dist):
    app=[]
    for mag in M:
        app.append(mag+5*np.log10(dist)-5)
    return(app)

def correct_for_dust(long, lat):
    """Query IRSA dust map for E(B-V) value and returns reddening array
    ----------
    wavelength : numpy array-like
        Wavelength values for which to return reddening
    ra : float
        Right Ascencion in degrees
    dec : float
        Declination in degrees

    Returns
    -------
    reddening : numpy array

    Notes
    -----
    For info on the dust maps, see http://irsa.ipac.caltech.edu/applications/DUST/
    """

    from astroquery.irsa_dust import IrsaDust
    import astropy.coordinates as coord
    import astropy.units as u
    C = coord.SkyCoord(long, lat, unit='deg', frame='galactic')
    dust_image = IrsaDust.get_images(C, radius=2 *u.deg, image_type='ebv', timeout=60)[0]
    ebv = np.mean(dust_image[0].data[40:42, 40:42])
    return ebv

def dust_correct(mag,ebv,band):
    correction_dictionary={'U':1.569,'B':1.337,'V':1.000,'R':0.751,'I':0.479,'J':0.282,'H':0.190,'K':0.114} #dictionnaire des coefficients de correction
    correct_coef=correction_dictionary[band]
    mag_correct=[]
    for m in mag:
        mag_correct.append(m+3.1*ebv*correct_coef)
    return mag_correct

def distrib_lat(z):
    H=15 #30° taille caractéristique du disque galactique
    return np.exp(-np.abs(z)/H)

###Core

##preprocess les données de 89 SN1BC

filename='SN1bc'
event=np.array(open(dirdata+filename+'.txt','r').read().split('\n')) #list de nom des évènements

type,ebv,lumdist,time,e_time,u_time,magnitude,e_magnitude,band=gather(event) #on collecte les données dans les listes suivantes

U,B,V,R,I=Band('U'),Band('B'),Band('V'),Band('R'),Band('I') #on crée les bandes

Tmax=maxVtime() #on recherche les maximums en bande V

#On rescale les temps
U.time_rescale(Tmax)
B.time_rescale(Tmax)
V.time_rescale(Tmax)
R.time_rescale(Tmax)
I.time_rescale(Tmax)

#on applique les corrections
U.correction()
B.correction()
V.correction()
R.correction()
I.correction()

#on passe en magnitude absolues
U.mag_abs()
B.mag_abs()
V.mag_abs()
R.mag_abs()
I.mag_abs()

#on rescale les magnitudes
U.mag_rescale()
B.mag_rescale()
V.mag_rescale()
R.mag_rescale()
I.mag_rescale()

#on sauve les magnitudes maximales dans un fichier pour plus tard
maxdata=''
for u in U.Maxabs:
    maxdata=maxdata+str(u)+'\n'
write(maxdata,dirtmp+'U_maxabs.txt')

maxdata=''
for b in B.Maxabs:
    maxdata=maxdata+str(b)+'\n'
write(maxdata,dirtmp+'B_maxabs.txt')

maxdata=''
for v in V.Maxabs:
    maxdata=maxdata+str(v)+'\n'
write(maxdata,dirtmp+'V_maxabs.txt')

maxdata=''
for r in R.Maxabs:
    maxdata=maxdata+str(r)+'\n'
write(maxdata,dirtmp+'R_maxabs.txt')

maxdata=''
for i in I.Maxabs:
    maxdata=maxdata+str(i)+'\n'
write(maxdata,dirtmp+'I_maxabs.txt')

mintime=[]
for t in U.Time:
    if len(t)<1:
        continue
    mintime.append(t[0])
np.savetxt(dirtmp+'U_starttime.txt',mintime)
print(np.mean(mintime))

mintime=[]
for t in B.Time:
    if len(t)<1:
        continue
    mintime.append(t[0])
np.savetxt(dirtmp+'B_starttime.txt',mintime)
print(np.mean(mintime))

mintime=[]
for t in V.Time:
    if len(t)<1:
        continue
    mintime.append(t[0])
np.savetxt(dirtmp+'V_starttime.txt',mintime)
print(np.mean(mintime))

mintime=[]
for t in R.Time:
    if len(t)<1:
        continue
    mintime.append(t[0])
np.savetxt(dirtmp+'R_starttime.txt',mintime)
print(np.mean(mintime))

mintime=[]
for t in I.Time:
    if len(t)<1:
        continue
    mintime.append(t[0])
np.savetxt(dirtmp+'I_starttime.txt',mintime)
print(np.mean(mintime))