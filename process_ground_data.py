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
    
    IMU_log = ''
    Meteon_log = ''
    merged_log = ''
    surface_data = ''

    TZ = 'UTC'
    MDT = 'US/Mountain'
    
    source_epsg = 'EPSG:4326'
    dest_epsg = ''
    
    spectral_bandwidth = ''
    
    def __init__(self, path_to_IMU_log, path_to_meteon_log, surface_data, local_utm_epsg, spectral_bandwidth):
        
        self.dest_epsg = local_utm_epsg
        
        self.spectral_bandwidth = spectral_bandwidth
        
        self.IMU_log = self.prep_DJI_log(path_to_IMU_log)
        
        self.Meteon_log = self.clean_Meteon_log(path_to_meteon_log)
        
        self.merged_log = self.merge_logs()
        
        self.merged_log = self.add_radiative_transfer_fields(self.merged_log)
        
        self.surface_data = surface_data
        
    
    def read_IMU_csv(self, path_to_dji_log):
        
        df = pd.read_csv('D:/field_data/YC/YC20210318/imu/YC20210318_imu_validation.txt', delimiter = ',', skiprows=[0])
        df.index = df["Record Time:"]
        
        df = df.drop(columns = ['ChipTime:', 'ax：', 'ay：', 'az：', 'wx：', 'wy：', 'wz：', 'Unnamed: 11'])
        
        df['AngleY：'] = df['AngleY：']
        
        df = df.groupby(df.index).mean()
        
        #calculate tilt and tilt direction
        tilt = [angles.get_tilt_witmotion(pitch, roll, yaw)[0] for (pitch, roll, yaw) in zip(df['AngleY：'], df['AngleX：'], df['AngleZ：']-yaw_offset)]
        
        tilt_dir = [angles.get_tilt_witmotion(pitch, roll, yaw)[1] for (pitch, roll, yaw) in zip(df['AngleY：'], df['AngleX：'], df['AngleZ：']-yaw_offset)]
        
        df['tilt'] = tilt
        df['tilt_dir'] = tilt_dir
        
        df.index = pd.DatetimeIndex(df.index)
        #df.to_csv('C:/Temp/IMU/Record2_processed.txt')
        
    
    def read_Meteon_csv(self, path_to_meteon_log):
        
        df_meteon = pd.read_excel('D:/field_data/YC/YC20210318/imu/YC20210318_validation.xls', usecols=[0,2,5], skiprows=9, 
                                  names = ["Time", "incoming (W/m^2)", "reflected (W/m^2)"], parse_dates=True, index_col = 'Time',
                                  sheet_name = None)
        
        for key in df_meteon:
    
            incoming = df_meteon[key]['incoming (W/m^2)']
            reflected = df_meteon[key]['reflected (W/m^2)']
            df_meteon[key]['albedo'] = reflected / incoming
            df_meteon[key] = pd.concat([df_meteon[key], df], axis=1, join='inner')
            df_meteon[key]
            df_meteon[key].to_csv('D:/field_data/YC/YC20210318/imu/' + key +'.csv')
        
        return pd.read_csv(path_to_meteon_log, usecols=[0,2,5], skiprows=9, names = ["Time", "incoming (W/m^2)", "reflected (W/m^2)"])
        
    def add_UTM_coordinates(self, df):
        
        projected_lon, projected_lat = process_util.convert_coordinates(self.source_epsg, self.dest_epsg, df['lon'], df['lat'])
        
        df['lon_utm'] = projected_lon
        df['lat_utm'] = projected_lat
        
        return df
    
    
    def prep_IMU_log(self, path_to_dji_log):

        df = self.read_DJI_csv(path_to_dji_log)
        
        df = df.rename(columns={'ChipTime:': 'datetime', 
                                'AngleX：': 'roll', 
                                'AngleY：': 'pitch', 
                                'AngleZ：': 'yaw'})
        
        #convert to mountain time
        df['datetime'] = pd.DatetimeIndex(df['datetime']).tz_convert(pytz.timezone(self.TZ))
    
        #flight logs collect on milliseconds, so we must average values over each second
        df = df.groupby(df['datetime']).mean()
        
        df = self.add_UTM_coordinates(df)
    
        return df
    
    def add_radiative_transfer_fields(self, df):
        
        df['6s_Direct_Irradiance_Proportion'] = np.zeros(df.shape[0])
        df['6s_Diffuse_Irradiance_Proportion'] = np.zeros(df.shape[0])
        df['6s_Solar_Zenith_Angle'] = np.zeros(df.shape[0])
        df['6s_Solar_Azimuth_Angle'] = np.zeros(df.shape[0])
        
        for index, row in df.iterrows():
            
            lat = row['lat']
            lon = row['lon']
            alt_m = row['alt_msl']
            dt = index
            
            p_dir, p_diff, solar_zenith, solar_azimuth = process_util.run_radiative_transfer(self.spectral_bandwidth, lat, lon, alt_m, dt)
            
            df.loc[index, '6s_Direct_Irradiance_Proportion'] = p_dir
            df.loc[index, '6s_Diffuse_Irradiance_Proportion'] = p_diff
            df.loc[index, '6s_Solar_Zenith_Angle'] = solar_zenith
            df.loc[index, '6s_Solar_Azimuth_Angle'] = solar_azimuth
        
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
        
    
    
        
  
    
    

