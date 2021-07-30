#!/usr/bin/env python

##Libraries

import os

file_dir=os.path.dirname(os.path.realpath('__file__')) #directory of the curent file
target_dir=os.path.join(file_dir,'bin')

##check and download files

#SN Ib/c
file_to_execute=os.path.join(target_dir,'download_events_files_SNIBC.py')
os.system(f'python {file_to_execute}')

file_to_execute=os.path.join(target_dir,'download_meta_photometry_SNIBC.py')
os.system(f'python {file_to_execute}')

"""
#SN II
file_to_execute=os.path.join(target_dir,'download_events_files_SNII.py')
os.system(f'python {file_to_execute}')

file_to_execute=os.path.join(target_dir,'download_meta_photometry_SNII.py')
os.system(f'python {file_to_execute}')
"""

##Filter the data

file_to_execute=os.path.join(target_dir,'filter_data_SNIBC.py')
os.system(f'python {file_to_execute}')

"""
#SN II
file_to_execute=os.path.join(target_dir,'filter_data_SNII.py')
os.system(f'python {file_to_execute}')
"""