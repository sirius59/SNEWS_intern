##Libraries

import os
import requests as req
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rv_discrete

##Function

def check_dir_and_create(target):
    target_dir=os.path.join(file_dir,target) #path of the targeted dir

    if not os.path.isdir(target_dir): #if no dir, create it
        os.mkdir(target_dir)

def mag_distrib(band): #save distribution graphics and return distribution
    check_dir_and_create('graph')
    target_file=os.path.join(dir_max_mag,f'max_mag_IBC_{band}.txt')
    save_file=os.path.join(file_dir,f'graph/mag_distrib_IBC_{band}.pdf')
    magnitude=[i for i in pd.read_csv(target_file,header=None)[0]]
    min=int(round(np.min(magnitude),0))
    max=int(round(np.max(magnitude),0)+1)
    delta=max-min
    bins=np.linspace(min,max,delta+1)

    plt.clf()
    probalist,binlist,c=plt.hist(magnitude,bins=bins,density=True,histtype='step')
    plt.xlabel('magnitudes absolues',fontsize=15)
    plt.ylabel('proportion',fontsize=15)
    plt.title(f'distribution des magnitudes absolues aux pics de luminosité des SN Ib/c en bande {band}',fontsize=17)
    plt.savefig(save_file, dpi=150, bbox_inches='tight')
    plt.clf()

    return rv_discrete(name=f'cstm{band}',values=(binlist[:-1],probalist))

def abs_to_app(mag,dist):
    mag+=5*np.log10(dist*1e6)-5
    return mag

def EBV(long, lat):
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

def dust_correction(magnitude,long,lat,band):
    correction_dictionary={'U':1.557,'B':1.306,'G':1.238,'V':0.997,'R':0.815,'I':0.589,'Y':0.391,'J':0.293,'H':0.184}
    kappa=correction_dictionary[band]
    ebv=EBV(long,lat)
    magnitude+=3.1*ebv*kappa
    return magnitude

def min_max_telescope(band):
    telescope_file=os.path.join(file_dir,'config/telescopes.txt')
    file=open(telescope_file,'r')
    names=file.read().split('\n')
    file.close()
    mag_OK=[]

    for tel in names:
        telescope_file=os.path.join(file_dir,f'config/{tel}.config')
        file=open(telescope_file,'r')
        tel_data=file.read().split('\n')
        file.close()
        filter=[i for i in tel_data if 'filt' in i][0].split(' ')[1]
        mag_tel=[i for i in tel_data if 'magnitude' in i][0].split(' ')[1]
        if band in filter.upper():
            mag_OK.append(float(mag_tel))
    if len(mag_OK)>0:
        return [np.min(mag_OK),np.max(mag_OK)]
    else:
        return [np.nan,np.nan]

##Core

requested_band=['U','G','R','I','Y','J','H','V']
file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
dir_max_mag=os.path.join(file_dir,'data/max_mag')
longitude=np.linspace(0,360,100)
dist=8 #kpc
lat=0

print('generating graphics')

for band in requested_band:
    save_mag_long=os.path.join(file_dir,f'graph/mag_VS_long_IBC_{band}.pdf')
    globals()[f'mag_distrib_{band}']=mag_distrib(band) #store in the variable mag_distrib_band the distribution associated with the band
    maximum_magnitude=globals()[f'mag_distrib_{band}'].rvs()
    maximum_magnitude=abs_to_app(maximum_magnitude,dist)
    MAG=[dust_correction(maximum_magnitude,i,lat,band) for i in longitude]
    plt.plot(longitude,MAG,'+')
    plt.title(f'Preliminary sensitivity threshold of GRANDMA instruments for 8kpc SN. Lat=0° in {band} band.',fontsize=17)
    plt.xlabel('Longitude in deg',fontsize=15)
    plt.ylabel('Apparent magnitude at the peak',fontsize=15)
    tel_sensitivity=min_max_telescope(band)
    if np.nan in tel_sensitivity:
        plt.text(50,np.min(MAG)+30,'No telescope equiped with this filter',fontsize=15)
    else:
        plt.plot([0,360],[tel_sensitivity[0],tel_sensitivity[0]],'k--')
        plt.plot([0,360],[tel_sensitivity[1],tel_sensitivity[1]],'k--')
        plt.text(362,tel_sensitivity[0]-2,'min',fontsize=15)
        plt.text(362,tel_sensitivity[1]+2,'max',fontsize=15)
    plt.ylim((np.min(MAG)-3,60))
    plt.gca().invert_yaxis()
    plt.savefig(save_mag_long, dpi=150, bbox_inches='tight')


