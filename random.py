## Import libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline,BPoly
from astropy.coordinates import SkyCoord
import astropy
from scipy.stats import rv_discrete

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

random_time=-10
random_maxabs=mag_distrib.rvs()
random_abs=relativ_magabs(random_time)
random_distance=dist_distrib.rvs()
random_long=np.random.uniform(0,360)
lat=np.linspace(-90,90,1000)
proba_lat=distrib_lat(lat)
norm_proba_lat=proba_lat/np.sum(proba_lat)
lat_distrib=rv_discrete(name='cstm3',values=(lat,norm_proba_lat))
random_lat=lat_distrib.rvs()
print(random_lat)
plt.plot(lat,norm_proba_lat)
plt.show()
constellation=SkyCoord(random_long,random_lat,unit='deg',frame='galactic').get_constellation()
ebv=correct_for_dust(random_long,random_lat)
Time,Mag=curve(random_time,random_abs)
Mag+=random_maxabs
Mag=abs_to_app(Mag,random_distance)
Mag=dust_correct(Mag,ebv,bandstr)
plt.plot(Time,Mag,label="ratio")
plt.legend()
plt.xlabel('temps en jours')
plt.ylabel('magnitude apparente')
plt.title('SN1 b/c dans '+ constellation+': distance= '+str(random_distance)+' Pc. Bande: '+bandstr)
plt.gca().invert_yaxis()
plt.show()