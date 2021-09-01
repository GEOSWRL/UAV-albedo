# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 16:16:49 2021

@author: x51b783
"""

from process_UAV import UAV_Albedo

path_to_dji_csv = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/dji_flight_logs/20210311_YC_FLY276.csv'
path_to_meteon_csv = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/radiometers/20210311_YC_Meteon_lawnmower.csv'
local_utm_epsg = 'EPSG:32612'
pyranometer_bandwidth = [0.31, 2.7] #in micrometers

ua = UAV_Albedo(path_to_dji_csv, path_to_meteon_csv, '', local_utm_epsg, pyranometer_bandwidth)

#convert to CSV

   