# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 16:16:49 2021

@author: x51b783
"""
from process_topographic_correction import Topographic_Correction
from process_surface_data import Surface_Data
from process_ground_data import Ground_Data
from process_UAV import UAV_Albedo
import pandas as pd
import seaborn as sns
import process_util as pu
import numpy as np

PATH_TO_DJI_CSV = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/dji_flight_logs/20210311_YC_FLY277.csv'
PATH_TO_METEON_CSV = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/radiometers/20210311_YC_Meteon_lawnmower.csv'
PATH_TO_OUTPUT_LOG = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/01_merged_datalogs/01_lawnmower_surveys/20210311_YC_FLY277_merged_testfile.csv'



PATH_TO_IMU_CSV = 'D:/UAV-albedo/data_test_dir/02_ground_validation/01_raw_data/IMU/20210311_YC_IMU_all.csv'
PATH_TO_GROUND_METEON = 'D:/UAV-albedo/data_test_dir/02_ground_validation/01_raw_data/radiometers/20210311_YC_Meteon_Ground.xls'
PATH_TO_GPS_DATA = 'D:/UAV-albedo/data_test_dir/02_ground_validation/01_raw_data/GPS/20210311_YC_IMU_GPS.csv'
PATH_TO_OUTPUT_IMU = 'D:/UAV-albedo/data_test_dir/02_ground_validation/02_processed_data/001_prepped_logs/20210311_prepped_imu_testfile.xlsx'

LOCAL_UTM_EPSG = 'EPSG:32612'
PYRANOMETER_BANDWIDTH = [0.31, 2.7] #in micrometers

SfM=Surface_Data('20210311_YC_TC_DSM.tif', 
                '20210311_YC_TC_Slope.tif', 
                '20210311_YC_TC_Aspect.tif', 
                '20210311_YC_LS8_Res.tif',
                '20210311_YC_TC_XCoords.tif', 
                '20210311_YC_TC_YCoords.tif') 
'''
def prep_uav_data():
    
    ua = UAV_Albedo(PATH_TO_DJI_CSV, PATH_TO_METEON_CSV, LOCAL_UTM_EPSG, PYRANOMETER_BANDWIDTH)

    ua.log_to_csv(PATH_TO_OUTPUT_LOG)
  

prepped_df=pd.read_csv(PATH_TO_OUTPUT_LOG, index_col='Unnamed: 0')

for index, row in prepped_df.iterrows():
    
    tc = Topographic_Correction(row, SfM, 'SfM', 140)
    
    tc.topo_correction()
    
    print(tc.corrected_albedo)
    print(tc.point_alt_agl)
    fp=tc.footprint
        
    gt = SfM.get_geotransform()
    print(np.nanmax(fp))
    pu.write_geotiff('D:/UAV-albedo/data_test_dir/temp_files/footprint.tif', 
                         np.shape(fp), gt, 32612, fp)
  
'''

def footprint_to_tiff(topo_correction):
        
        fp=tc.footprint    
    
        gt = SfM.get_geotransform()
        
        pu.write_geotiff('D:/UAV-albedo/data_test_dir/temp_files/footprint.tif', 
                         np.shape(fp), gt, 32612, fp)

def prep_imu_data():

    gd = Ground_Data(PATH_TO_IMU_CSV, PATH_TO_GROUND_METEON, PATH_TO_GPS_DATA, LOCAL_UTM_EPSG, PYRANOMETER_BANDWIDTH)
    
    gd.log_to_excel(PATH_TO_OUTPUT_IMU)

prepped_df=pd.read_excel(PATH_TO_OUTPUT_IMU, index_col='Unnamed: 0',sheet_name = None)

for key in prepped_df:
    
    for index, row in prepped_df[key].iterrows():
        
        tc = Topographic_Correction(row, SfM, 'SfM', 178, point_alt_agl=1.5, gps_point_on_ground = True)
        
        tc.topo_correction()
        
        
        break
    break
        















