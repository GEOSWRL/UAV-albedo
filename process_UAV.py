# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 14:51:43 2021

@author: x51b783
"""
import pandas as pd
import pytz
import process_util
import numpy as np


class UAV_Albedo:
    
    DJI_log = ''
    Meteon_log = ''
    merged_log = ''
    surface_data = ''

    TZ = 'UTC'
    MDT = 'US/Mountain'
    
    source_epsg = 'EPSG:4326'
    dest_epsg = ''
    
    spectral_bandwidth = ''
    
    def __init__(self, path_to_dji_log, path_to_meteon_log, surface_data, local_utm_epsg, spectral_bandwidth):
        
        self.dest_epsg = local_utm_epsg
        
        self.spectral_bandwidth = spectral_bandwidth
        
        self.DJI_log = self.prep_DJI_log(path_to_dji_log)
        
        self.Meteon_log = self.clean_Meteon_log(path_to_meteon_log)
        
        self.merged_log = self.merge_logs()
        
        self.merged_log = self.add_radiative_transfer_fields(self.merged_log)
        
        self.surface_data = surface_data
        
    
    def read_DJI_csv(self, path_to_dji_log):
        
        return pd.read_csv(path_to_dji_log, usecols=['GPS:dateTimeStamp', 'IMU_ATTI(0):roll:C', 'IMU_ATTI(0):pitch:C', 'IMU_ATTI(0):yaw:C', 'IMU_ATTI(0):velComposite:C', 'IMU_ATTI(0):tiltInclination:C', 'IMU_ATTI(0):tiltDirectionEarthFrame:C', 'IMU_ATTI(0):tiltDirectionBodyFrame:C', 'GPS:Long', 'GPS:Lat', 'GPS:heightMSL', 'GPS:dateTimeStamp'], header=0)
        
    
    def read_Meteon_csv(self, path_to_meteon_log):
        
        return pd.read_csv(path_to_meteon_log, usecols=[0,2,5], skiprows=9, names = ["Time", "incoming (W/m^2)", "reflected (W/m^2)"])
        
    def add_UTM_coordinates(self, df):
        
        projected_lon, projected_lat = process_util.convert_coordinates(self.source_epsg, self.dest_epsg, df['GPS:Long'], df['GPS:Lat'])
        
        df['lon_utm'] = projected_lon
        df['lat_utm'] = projected_lat
        
        return df
    
    def add_radiative_transfer_fields(self, df):
        
        df['6s_Direct_Irradiance_Proportion'] = np.zeros(df.shape[0])
        df['6s_Diffuse_Irradiance_Proportion'] = np.zeros(df.shape[0])
        df['6s_Solar_Zenith_Angle'] = np.zeros(df.shape[0])
        df['6s_Solar_Azimuth_Angle'] = np.zeros(df.shape[0])
        
        for index, row in df.iterrows():
            
            lat = row['GPS:Lat']
            lon = row['GPS:Long']
            alt_m = row['GPS:heightMSL']
            dt = index
            
            p_dir, p_diff, solar_zenith, solar_azimuth = process_util.run_radiative_transfer(self.spectral_bandwidth, lat, lon, alt_m, dt)
            
            df.loc[index, '6s_Direct_Irradiance_Proportion'] = p_dir
            df.loc[index, '6s_Diffuse_Irradiance_Proportion'] = p_diff
            df.loc[index, '6s_Solar_Zenith_Angle'] = solar_zenith
            df.loc[index, '6s_Solar_Azimuth_Angle'] = solar_azimuth
        
        return df
        
    def prep_DJI_log(self, path_to_dji_log):

        df = self.read_DJI_csv(path_to_dji_log)
        
        #convert to mountain time
        df['GPS:dateTimeStamp'] = pd.DatetimeIndex(df['GPS:dateTimeStamp']).tz_convert(pytz.timezone(self.TZ))
    
        #flight logs collect on milliseconds, so we must average values over each second
        df = df.groupby(df['GPS:dateTimeStamp']).mean()
        
        df = self.add_UTM_coordinates(df)
    
        return df
        
    
    def clean_Meteon_log(self, path_to_meteon_log):
        
        df = self.read_Meteon_csv(path_to_meteon_log)        

        #correct downward faceing sensor for leg interference
        reflected_corr = df['reflected (W/m^2)'].multiply(1.0197)
        df.insert(3,'albedo', reflected_corr.div(df['incoming (W/m^2)'])) #calculate albedo
        
        df['Time'] = pd.DatetimeIndex(df['Time']).tz_localize(None)

        df['Time'] = pd.DatetimeIndex(df['Time']).tz_localize(pytz.timezone(self.MDT))

        df['Time'] = pd.DatetimeIndex(df['Time']).tz_convert(pytz.timezone(self.TZ))

        df.set_index('Time', inplace=True)
        
        return df
    
    def merge_logs(self):
        
        return pd.concat([self.DJI_log, self.Meteon_log], axis=1, join='inner')
        
    def get_DJI_log(self):
        
        return self.DJI_log

    def log_to_csv(self, path_to_output_csv):
        
        self.merged_log.to_csv(path_to_output_csv)
        
    
    
        
  
    
    