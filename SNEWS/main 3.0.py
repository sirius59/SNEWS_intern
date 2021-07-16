###Libraries

from scipy.stats import rv_discrete

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

def curve(t,random_abs):
    ratio=(globals()[f'{in_bande}'].Mean(t)-random_abs)/(globals()[f'{in_bande}'].Mean(t)-globals()[f'{in_bande}'].Slow(t))
    time=np.linspace(t,30,1000)
    lightcurve=[random_abs]
    for temps in time[1:]:
        lightcurve.append(globals()[f'{in_bande}'].Mean(temps)-ratio*(globals()[f'{in_bande}'].Mean(temps)-globals()[f'{in_bande}'].Slow(temps)))
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
        self.Exposuretime=float([i for i in telescope_data if 'exposuretime' in i][0].split(' ')[1])
        self.Latitude=float([i for i in telescope_data if 'latitude' in i][0].split(' ')[1])
        self.Longitude=float([i for i in telescope_data if 'longitude' in i][0].split(' ')[1])
        self.Elevation=float([i for i in telescope_data if 'elevation' in i][0].split(' ')[1])

###Directories

dir='C:\\Users\\cleme\\Desktop\\SNEWS\\'
dirconfig='C:\\Users\\cleme\\Desktop\\SNEWS\\config\\'

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

random_maxabs=globals()[f'{in_bande}'].Distrib.rvs() #on tire une magnitude absolue max dans la distribution
random_abs=relativ_magabs(t0) #on tire une magnitude absolue relative selon une loi normal centré sur la courbe moyenne
ebv=correct_for_dust(long,lat)
plt.clf()

for dist in dist_list:
    Time,Mag=curve(t0,random_abs)
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
T=[t0,30]

for tel in telescope_OK:
    tel_mag=[globals()[f'{tel}'].Magnitude,globals()[f'{tel}'].Magnitude]
    plt.plot(T,tel_mag,'k--')
    plt.text(31,tel_mag[0],tel)

plt.xlabel('temps en jours')
plt.legend()
plt.ylabel('magnitude apparente')
plt.gca().invert_yaxis()
plt.title(f'seuil de sensibilité des instruments pour une SN donnée. long={long}°, lat={lat}° en bande {in_bande}')
plt.show()

long_list=np.linspace(0,360,100)
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
plt.yscale('log')
plt.ylabel('magnitude apparente au pic')
plt.xlabel('longitude en deg')
plt.title(f'seuil de sensibilité des instruments pour une SN à 8 kPc et lat=0° en bande {in_bande}')
plt.show()