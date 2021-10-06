#!/usr/bin/env python

##Libraries

import os

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
target_dir=os.path.join(file_dir,'bin')

##check and download files

file_to_execute=os.path.join(target_dir,'download_events_files_SNIBC.py') #download the name of all SN IBC events in /download/events_IBC.csv file
os.system(f'python {file_to_execute}')

file_to_execute=os.path.join(target_dir,'download_meta_photometry_SNIBC.py') #download the meta data and the photometry of all events in the previous file in /download/tmp/meta or photometry directory (TSV files)
os.system(f'python {file_to_execute}')

##Filter the data

file_to_execute=os.path.join(target_dir,'filter_data_SNIBC.py') #ignore event with a lack of data to be used and write the name of good events to use depending on the band in /data/IBC/events_IBC_{band}.csv file
os.system(f'python {file_to_execute}')

#format bands in upper case
file_to_execute=os.path.join(target_dir,'format_band.py')
os.system(f'python {file_to_execute}')

file_to_execute=os.path.join(target_dir,'photo_band_check.py') #check if the previous events have enough photometric data to be used and rewrite the correct list of event in the previous file + enumerate all the events used no matter the band
os.system(f'python {file_to_execute}')

##get the maximum magnitude
file_to_execute=os.path.join(target_dir,'max_mag.py')
os.system(f'python {file_to_execute}')

##making plots
##mag vs long
file_to_execute=os.path.join(target_dir,'mag_vs_long.py')
os.system(f'python {file_to_execute}')

##distance
file_to_execute=os.path.join(target_dir,'distance.py')
os.system(f'python {file_to_execute}')


##Curve
file_to_execute=os.path.join(target_dir,'curve.py')
os.system(f'python {file_to_execute}')