##Libraries

import numpy as np
import requests as req
from astropy.time import Time
import matplotlib.pyplot as plt

##Variables

dir='C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\' #chemin du directory
event=np.array(open(dir+'SN1BC_names.txt','r').read().split('\n')) #list de nom des évènements

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


##functions

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
        write(metadata_request,dir+'meta_tmp.txt')
        metadata=read_meta(dir+'meta_tmp.txt')

        type.append(metadata[3])
        ebv.append(float(metadata[8]))
        lumdist.append(float(metadata[15]))

        photometry_request=req.get(f'https://api.astrocats.space/{name}/photometry/time+e_time+u_time+magnitude+e_magnitude+band+upperlimit?format=tsv').text
        write(photometry_request,dir+'photometry_tmp.txt')
        photometry=read_photometry(dir+'photometry_tmp.txt')

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



##core

type,ebv,lumdist,time,e_time,u_time,magnitude,e_magnitude,band=gather(event) #on collecte les données dans les listes suivantes

U,B,V,R,I,J,H,K=Band('U'),Band('B'),Band('V'),Band('R'),Band('I'),Band('J'),Band('H'),Band('K') #on crée les bandes

Tmax=maxVtime() #on recherche les maximums en bande V

#On rescale les temps
U.time_rescale(Tmax)
B.time_rescale(Tmax)
V.time_rescale(Tmax)
R.time_rescale(Tmax)
I.time_rescale(Tmax)
J.time_rescale(Tmax)
H.time_rescale(Tmax)
K.time_rescale(Tmax)

#on applique les corrections
U.correction()
B.correction()
V.correction()
R.correction()
I.correction()
J.correction()
H.correction()
K.correction()

#on passe en magnitude absolues
U.mag_abs()
B.mag_abs()
V.mag_abs()
R.mag_abs()
I.mag_abs()
J.mag_abs()
H.mag_abs()
K.mag_abs()


#on rescale les magnitudes
U.mag_rescale()
B.mag_rescale()
V.mag_rescale()
R.mag_rescale()
I.mag_rescale()
J.mag_rescale()
H.mag_rescale()
K.mag_rescale()

#on sauve les magnitudes maximales dans un fichier pour plus tard
maxdata=[]
for u in U.Maxabs:
    maxdata.append(u)
np.savetxt(dir+'U_maxabs.txt',np.array(maxdata))

maxdata=''
for b in B.Maxabs:
    maxdata=maxdata+str(b)+'\n'
write(maxdata,dir+'B_maxabs.txt')

maxdata=''
for v in V.Maxabs:
    maxdata=maxdata+str(v)+'\n'
write(maxdata,dir+'V_maxabs.txt')

maxdata=''
for r in R.Maxabs:
    maxdata=maxdata+str(r)+'\n'
write(maxdata,dir+'R_maxabs.txt')

maxdata=''
for i in I.Maxabs:
    maxdata=maxdata+str(i)+'\n'
write(maxdata,dir+'I_maxabs.txt')

maxdata=''
for j in J.Maxabs:
    maxdata=maxdata+str(j)+'\n'
write(maxdata,dir+'J_maxabs.txt')

maxdata=''
for h in H.Maxabs:
    maxdata=maxdata+str(h)+'\n'
write(maxdata,dir+'H_maxabs.txt')

maxdata=''
for k in K.Maxabs:
    maxdata=maxdata+str(k)+'\n'
write(maxdata,dir+'K_maxabs.txt')

#on sauve les courbes de lumière dans un fichier pour exectuer dans un script séparé
data=''
for i in range(len(U.Time)):
    for j in range(len(U.Time[i])):
        data=data+str(U.Time[i][j])+'\t'+str(U.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'U.txt')

data=''
for i in range(len(B.Time)):
    for j in range(len(B.Time[i])):
        data=data+str(B.Time[i][j])+'\t'+str(B.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'B.txt')

data=''
for i in range(len(V.Time)):
    for j in range(len(V.Time[i])):
        data=data+str(V.Time[i][j])+'\t'+str(V.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'V.txt')

data=''
for i in range(len(R.Time)):
    for j in range(len(R.Time[i])):
        data=data+str(R.Time[i][j])+'\t'+str(R.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'R.txt')

data=''
for i in range(len(I.Time)):
    for j in range(len(I.Time[i])):
        data=data+str(I.Time[i][j])+'\t'+str(I.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'I.txt')

data=''
for i in range(len(J.Time)):
    for j in range(len(J.Time[i])):
        data=data+str(J.Time[i][j])+'\t'+str(J.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'J.txt')

data=''
for i in range(len(H.Time)):
    for j in range(len(H.Time[i])):
        data=data+str(H.Time[i][j])+'\t'+str(H.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'H.txt')

data=''
for i in range(len(K.Time)):
    for j in range(len(K.Time[i])):
        data=data+str(K.Time[i][j])+'\t'+str(K.Magnitude[i][j])+'\n'
    data=data+'/'+'\n'
write(data,dir+'K.txt')

##partie pas utile pour la suite (mais utile pour vérifier)
for r in range(len(event)):
    plt.plot(U.Time[r],U.Magnitude[r],'.',label=U.Name)
    plt.plot(B.Time[r],B.Magnitude[r],'.',label=B.Name)
    plt.plot(V.Time[r],V.Magnitude[r],'.',label=V.Name)
    plt.plot(R.Time[r],R.Magnitude[r],'.',label=R.Name)
    plt.plot(I.Time[r],I.Magnitude[r],'.',label=I.Name)
    plt.plot(J.Time[r],J.Magnitude[r],'.',label=J.Name)
    plt.plot(H.Time[r],H.Magnitude[r],'.',label=H.Name)
    plt.plot(K.Time[r],K.Magnitude[r],'.',label=K.Name)
    plt.legend()
    plt.xlabel('temps en jours')
    plt.ylabel('Magnitude absolue')
    plt.title(U.Event[r])
    plt.gca().invert_yaxis()
    plt.show()