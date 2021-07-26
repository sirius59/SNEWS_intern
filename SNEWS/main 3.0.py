###Libraries

from scipy.stats import rv_discrete
from scipy.optimize import curve_fit

##Functions

def relativ_magabs(t):
    mu=globals()[f'{in_bande}'].Mean(t)
    sigma=abs(globals()[f'{in_bande}'].Fast(t)-globals()[f'{in_bande}'].Slow(t))/6
    return np.random.normal(mu,sigma)

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

def curve(t,T,random_abs):
    ratio=(globals()[f'{in_bande}'].Mean(t)-random_abs)/(globals()[f'{in_bande}'].Mean(t)-globals()[f'{in_bande}'].Fast(t))
    time=np.linspace(t,T,1000)
    lightcurve=[random_abs]
    for temps in time[1:]:
        lightcurve.append(globals()[f'{in_bande}'].Mean(temps)-ratio*(globals()[f'{in_bande}'].Mean(temps)-globals()[f'{in_bande}'].Fast(temps)))
    return(time,np.array(lightcurve))

def abs_to_app(M,dist):
    app=[]
    for mag in M:
        app.append(mag+5*np.log10(dist)-5)
    return(app)

def dust_correct(mag,ebv,band):
    correction_dictionary={'U':1.569,'B':1.337,'V':1.000,'R':0.751,'I':0.479,'J':0.282,'H':0.190,'K':0.114} #dictionnaire des coefficients de correction
    correct_coef=correction_dictionary[band]
    mag_correct=[]
    for m in mag:
        mag_correct.append(m+3.1*ebv*correct_coef)
    return mag_correct

def filter_select(filter):
    telescope_OK=[]
    for tel in telescope_list:
        if (filter.upper() in globals()[f'{tel}'].Filter.upper()):
            telescope_OK.append(tel)
        else:
            continue
    return telescope_OK

def distrib_lat(z):
    H=15 #30° taille caractéristique du disque galactique
    return np.exp(-np.abs(z)/H)

##Objects

class telescope:

    def __init__(self,name):
        self.Name=name
        config_file=open(dirconfig+name+'.config','r')
        telescope_data=config_file.read().split('\n')
        config_file.close()
        self.Filter=[i for i in telescope_data if 'filt' in i][0].split(' ')[1]
        if 'g' in self.Filter:
            self.Filter+='v'
        self.Magnitude=float([i for i in telescope_data if 'magnitude' in i][0].split(' ')[1])

###Directories

dir='C:\\Users\\cleme\\Desktop\\SNEWS\\'
dirconfig='C:\\Users\\cleme\\Desktop\\SNEWS\\config\\'
dirdata='C:\\Users\\cleme\\Desktop\\SNEWS\\data\\'

###Core
exec(open(dir+'fast_slow_mean.py','r').read()) #execution du script fast_slow_mean

t0=-5 #pourra être redéfini à l'aide des fits avec la formule de l'article
dist_list=np.array([1,5,10,15,20,25])*1e3
long=60
lat=0

##définie les distributions des maximum en magnitudes absolues pour chaque bandes

for i in ('B','V','R','I'):
    globals()[f'{i}_maxabs']=np.loadtxt(dirtmp+i+'_maxabs.txt')
    min=int(round(np.min(globals()[f'{i}_maxabs']),0))
    max=int(round(np.max(globals()[f'{i}_maxabs']),0)+1)
    delta=max-min
    bins=np.linspace(min,max,delta+1)

    probalist,binlist,c=plt.hist(globals()[f'{i}_maxabs'],bins=bins,density=True,histtype='step')
    globals()[f'{i}'].Proba=probalist
    globals()[f'{i}'].Bins=binlist
    globals()[f'{i}'].Distrib=rv_discrete(name=f'cstm{i}',values=(binlist[:-1],probalist))

in_bande=str(input('choix de la bande à observer (B,V,R,I): ')).upper()

plt.clf()

random_maxabs=globals()[f'{in_bande}'].Distrib.rvs() #on tire une magnitude absolue max dans la distribution
random_abs=relativ_magabs(t0) #on tire une magnitude absolue relative selon une loi normal centré sur la courbe moyenne
ebv=correct_for_dust(long,lat)

x=np.linspace(t0,25,1000)
Time,Mag=curve(t0,25,random_abs)
plt.plot(x,globals()[f'{in_bande}'].Slow(x),label='slow')
plt.plot(x,globals()[f'{in_bande}'].Fast(x),label='fast')
plt.plot(x,globals()[f'{in_bande}'].Mean(x),label='mean')
plt.plot(Time,Mag,label='generated')
plt.legend()
plt.xlabel('time in days',fontsize=15)
plt.ylabel('relative magnitude',fontsize=15)
plt.title('Generated curve',fontsize=15)
plt.gca().invert_yaxis()
plt.show()


for dist in dist_list:
    Time,Mag=curve(t0,25,random_abs)
    Mag+=random_maxabs
    Mag=abs_to_app(Mag,dist)
    Mag=dust_correct(Mag,ebv,in_bande)

    plt.plot(Time,Mag,label=str(dist/1e3)+'kPc')


##récupère les infos des télescopes
telescope_file=open(dirconfig+'telescopes.txt')
telescope_list=telescope_file.read().split('\n')
telescope_file.close()

for tel in telescope_list:
    globals()[f'{tel}']=telescope(tel) #crée les objets pour chaque télescopes de la liste

telescope_OK=filter_select(in_bande)
T=[t0,25]

for tel in telescope_OK:
    tel_mag=[globals()[f'{tel}'].Magnitude,globals()[f'{tel}'].Magnitude]
    plt.plot(T,tel_mag,'k--')
    plt.text(26,tel_mag[0],tel)

plt.xlabel('time in days',fontsize=15)
plt.legend()
plt.ylabel('apparent magnitude',fontsize=15)
plt.gca().invert_yaxis()
plt.title(f'Sensibility threshold of instruments for a given SN. long={long}°, lat={lat}° in {in_bande} band',fontsize=15)
plt.show()

long_list=np.linspace(0,360,300)
dist=8e3
max_mag_list=[]

for longitude in long_list:
    ebv=correct_for_dust(longitude,0)
    mag=[random_maxabs]
    mag=abs_to_app(mag,dist)
    mag=dust_correct(mag,ebv,in_bande)
    max_mag_list.append(mag[0])

plt.plot(long_list,max_mag_list,'+')

T=[0,360]
mag=[]
for tel in telescope_OK:
    mag.append(globals()[f'{tel}'].Magnitude)

plt.plot(T,[np.max(mag),np.max(mag)],'k--')
plt.text(363,np.max(mag),'max')
plt.plot(T,[np.min(mag),np.min(mag)],'k--')
plt.text(363,np.min(mag),'min')
plt.gca().invert_yaxis()
#plt.yscale('log')
plt.ylabel('apparent magnitude at the peak',fontsize=15)
plt.xlabel('longitude in deg',fontsize=15)
plt.title(f'Preliminary sensibility threshold of instruments for a 8 kPc SN. lat=0° in {in_bande} band',fontsize=15)
plt.show()

##importe distance distribution + MC simulation
data=np.loadtxt(dirdata+'distance_distrib.txt',delimiter=';')
dist=data[:,0]*1e3 #distances en kPc convertie en Pc
proba=np.abs(data[:,1])# qq points <0 mais quasi 0

normproba=proba/np.sum(proba)

dist_distrib=rv_discrete(name='cstm',values=(dist,normproba))

lat=np.linspace(-90,90,1000)
proba_lat=distrib_lat(lat)
norm_proba_lat=proba_lat/np.sum(proba_lat)
lat_distrib=rv_discrete(name='cstm3',values=(lat,norm_proba_lat))

N=10

MC_lat=lat_distrib.rvs(size=N)
MC_dist=dist_distrib.rvs(size=N)
MC_long=np.random.uniform(0,360,size=N)

MC_maxabs=globals()[f'{in_bande}'].Distrib.rvs(size=N) #on tire une magnitude absolue max dans la distribution
MC_rel_abs=relativ_magabs(t0) #on tire une magnitude absolue relative selon une loi normal centré sur la courbe moyenne
MC_ebv=np.array([correct_for_dust(MC_long[i],MC_lat[i]) for i in range(N)])

MC_mag=[]
for i in range(N):
    Time,Mag=curve(t0,25,MC_rel_abs)
    Mag=np.min(Mag)
    Mag+=MC_maxabs[i]
    Mag=abs_to_app([Mag],MC_dist[i])
    Mag=dust_correct([Mag],MC_ebv[i],in_bande)
    MC_mag.append(float(Mag[0]))

T=[0,1]

bins_list=np.linspace(-7,30,(30+7)*4)
plt.hist(MC_mag,density=True,cumulative=True,bins=bins_list)
plt.plot([np.max(mag),np.max(mag)],T,'k--')
plt.text(np.max(mag),1.1,'max')
plt.plot([np.min(mag),np.min(mag)],T,'k--')
plt.text(np.min(mag),1.1,'min')
plt.xlabel('magnitude apparente',fontsize=15)
plt.ylabel('cumulative proportion',fontsize=15)
plt.title(f'distribution cumulée des magnitudes apparentes. bande: {in_bande}',fontsize=15)
plt.show()
