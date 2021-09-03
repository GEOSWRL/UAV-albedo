# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 16:16:49 2021

@author: x51b783
"""
from process_topographic_correction import Topographic_Correction
from process_surface_data import Surface_Data
from process_UAV import UAV_Albedo
import pandas as pd

PATH_TO_DJI_CSV = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/dji_flight_logs/20210311_YC_FLY277.csv'
PATH_TO_METEON_CSV = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/radiometers/20210311_YC_Meteon_lawnmower.csv'
PATH_TO_OUTPUT_LOG = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/01_merged_datalogs/01_lawnmower_surveys/20210311_YC_FLY277_merged.csv'

LOCAL_UTM_EPSG = 'EPSG:32612'
PYRANOMETER_BANDWIDTH = [0.31, 2.7] #in micrometers


def prep_uav_data(path_to_output):
    ua = UAV_Albedo(PATH_TO_DJI_CSV, PATH_TO_METEON_CSV, '', LOCAL_UTM_EPSG, PYRANOMETER_BANDWIDTH)

    ua.log_to_csv(PATH_TO_OUTPUT_LOG)

sd=Surface_Data('20210311_YC_TC_DSM.tif', '20210311_YC_TC_Slope.tif', '20210311_YC_TC_Aspect.tif', '20210311_YC_LS8_Res.tif',
                       '20210311_YC_TC_XCoords.tif', '20210311_YC_TC_YCoords.tif') 

prepped_df=pd.read_csv('D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/01_merged_datalogs/01_lawnmower_surveys/20210311_YC_FLY277_merged.csv', index_col='Unnamed: 0')



for index, row in prepped_df.iterrows():
    tc = Topographic_Correction(row, sd, 'SfM', 140)
    print(tc.topo_correction() - tc.weighted_ls8)