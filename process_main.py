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

PATH_TO_DJI_CSV = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/dji_flight_logs/20210428_YC_FLY299.csv'
PATH_TO_METEON_CSV = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/01_raw_data/radiometers/20210428_YC_Meteon_lawnmower.csv'
PATH_TO_OUTPUT_LOG = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/01_merged_datalogs/01_lawnmower_surveys/20210428_YC_FLY299_merged.csv'
PATH_TO_PREPPED_LOG = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/01_merged_datalogs/04_vertical_transects_cleaned/20210428_YC_VT5.csv'

PATH_TO_IMU_CSV = 'D:/UAV-albedo/data_test_dir/02_ground_validation/01_raw_data/IMU/20210311_YC_IMU_all.csv'
PATH_TO_GROUND_METEON = 'D:/UAV-albedo/data_test_dir/02_ground_validation/01_raw_data/radiometers/20210311_YC_Meteon_Ground.xls'
PATH_TO_GPS_DATA = 'D:/UAV-albedo/data_test_dir/02_ground_validation/01_raw_data/GPS/20210311_YC_IMU_GPS.csv'
PATH_TO_OUTPUT_IMU = 'D:/UAV-albedo/data_test_dir/02_ground_validation/02_processed_data/001_prepped_logs/20210311_prepped_imu.xlsx'

LOCAL_UTM_EPSG = 'EPSG:32612'
PYRANOMETER_BANDWIDTH = [0.31, 2.7] #in micrometers

SfM=Surface_Data('20210428_YC_TC_DSM.tif', 
                '20210428_YC_TC_Slope.tif', 
                '20210428_YC_TC_Aspect.tif', 
                '20210428_YC_LS8_Res.tif',
                '20210428_YC_TC_XCoords.tif', 
                '20210428_YC_TC_YCoords.tif') 

def prep_uav_data():
    
    ua = UAV_Albedo(PATH_TO_DJI_CSV, PATH_TO_METEON_CSV, LOCAL_UTM_EPSG, PYRANOMETER_BANDWIDTH)

    ua.log_to_csv(PATH_TO_OUTPUT_LOG)
    

def prep_ground_data():

    gd = Ground_Data(PATH_TO_IMU_CSV, PATH_TO_GROUND_METEON, PATH_TO_GPS_DATA, LOCAL_UTM_EPSG, PYRANOMETER_BANDWIDTH)
    
    gd.log_to_excel(PATH_TO_OUTPUT_IMU)
    
  
def process_uav_data(topo_data_source, pfov):
    prepped_df=pd.read_csv(PATH_TO_PREPPED_LOG, index_col='Unnamed: 0')
    
    prepped_df['alt_agl'] = np.zeros(len(prepped_df))
    prepped_df['PFOV'] = np.zeros(len(prepped_df))
    prepped_df['corrected_albedo'] = np.zeros(len(prepped_df))
    prepped_df['ls8_albedo'] = np.zeros(len(prepped_df))
    prepped_df['topo_data_source'] = [topo_data_source]*len(prepped_df)
    
    for index, row in prepped_df.iterrows():
        
        tc = Topographic_Correction(row, SfM, topo_data_source, pfov)
        
        tc.topo_correction()
        
        prepped_df.loc[index, 'alt_agl'] = tc.point_alt_agl
        prepped_df.loc[index, 'PFOV'] = tc.PFOV
        prepped_df.loc[index, 'corrected_albedo'] = tc.corrected_albedo
        prepped_df.loc[index, 'ls8_albedo'] = tc.weighted_ls8
        
    return prepped_df


def process_ground_data(topo_data_source, pfov):
    prepped_df=pd.read_excel(PATH_TO_OUTPUT_IMU, index_col='Unnamed: 0', sheet_name = None)
    
    for key in prepped_df:
        
        prepped_df[key]['corrected_albedo'] = np.zeros(len(prepped_df[key]))
        prepped_df[key]['ls8_albedo'] = np.zeros(len(prepped_df[key]))
        prepped_df[key]['topo_data_source'] = [topo_data_source]*len(prepped_df[key])
        
        for index, row in prepped_df[key].iterrows():
            
            tc = Topographic_Correction(row, SfM, topo_data_source, pfov, point_alt_agl=1.5, gps_point_on_ground = True)
            
            tc.topo_correction()
            
            prepped_df[key].loc[index, 'corrected_albedo'] = tc.corrected_albedo
            prepped_df[key].loc[index, 'ls8_albedo'] = tc.weighted_ls8
    
    return prepped_df

def footprint_to_tiff(topo_correction):
        
        fp=topo_correction.footprint    
    
        gt = SfM.get_geotransform()
        
        pu.write_geotiff('D:/UAV-albedo/data_test_dir/temp_files/footprint.tif', 
                         np.shape(fp), gt, 32612, fp)

def fov_sensitivity_analysis(topo_data_source, data_type = 'UAV'):
    
    pfovs = np.arange(30, 180, 2.5)
    
    df = pd.DataFrame(columns = ['uncorrected_albedo', 'corrected_albedo', 'ls8_albedo','alt_agl',
                                 'PFOV', 'uncorrected_raw_error', 
                                 'corrected_raw_error'])

    for pfov in pfovs:
        print('processing for PFOV = ' + str(pfov))
        if data_type == 'UAV':
            
            df_pfov = process_uav_data(topo_data_source, pfov)
            
            df = df.append(pd.DataFrame({'uncorrected_albedo' : df_pfov['albedo'], 
                            'corrected_albedo' : df_pfov['corrected_albedo'],
                            'ls8_albedo' : df_pfov['ls8_albedo'],
                            'alt_agl' : df_pfov['alt_agl'],
                            'PFOV' : df_pfov['PFOV'],
                            'uncorrected_raw_error' : df_pfov['ls8_albedo'] - df_pfov['albedo'],
                            'corrected_raw_error' : df_pfov['ls8_albedo'] - df_pfov['corrected_albedo']}))
            
    return df


df = fov_sensitivity_analysis('SfM')
df.to_csv('D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/02_corrected_albedo/02_vertical_transects/02_FOV/20210428_YC_VT5_FOV.csv')

















