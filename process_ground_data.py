# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 14:51:43 2021

@author: x51b783
"""
import pandas as pd
import pytz
import process_util
import numpy as np
import process_util as pu

class Ground_Data:
    
    PATH_TO_IMU_LOG = ''
    PATH_TO_METEON_LOG = ''
    PATH_TO_GPS_LOG = ''
    
    Meteon_log = ''
    IMU_log = ''
    GPS_log = ''
    merged_log = ''

    TO_TZ = 'UTC'
    FROM_TZ = 'US/Mountain'
    
    source_epsg = 'EPSG:4326'
    dest_epsg = ''
    
    spectral_bandwidth = ''
    
    def __init__(self, path_to_IMU_log, path_to_meteon_log, path_to_gps_log, local_utm_epsg, spectral_bandwidth, GPS_data_present = False, path_to_merged_log = ''):
        
        if not GPS_data_present:
        
            self.PATH_TO_IMU_LOG = path_to_IMU_log
            
            self.PATH_TO_METEON_LOG = path_to_meteon_log
            
            self.PATH_TO_GPS_LOG = path_to_gps_log
            
            self.dest_epsg = local_utm_epsg
            
            self.spectral_bandwidth = spectral_bandwidth
        
            self.IMU_log = self.prep_IMU_log(self.PATH_TO_IMU_LOG)
        
            self.Meteon_log = self.prep_Meteon_log(self.PATH_TO_METEON_LOG)
        
            self.merged_log = self.merge_logs(self.IMU_log, self.Meteon_log)
            
            self.GPS_log = self.read_gps_data(self.PATH_TO_GPS_LOG)
            
            self.merged_log = self.append_gps_data(self.GPS_log, self.merged_log)
            
            self.merged_log = self.add_UTM_coordinates(self.merged_log)
            
            self.merged_log = self.add_radiative_transfer_fields(self.merged_log)
            
            
        
    def read_IMU_csv(self, path_to_imu_log):
        
        df = pd.read_csv(path_to_imu_log, delimiter = ',', skiprows=[0])
        
        df = df.drop(columns = ['ChipTime:', 'ax：', 'ay：', 'az：', 'wx：', 'wy：', 'wz：', 'Unnamed: 11'])
        
        return df
    
    def prep_IMU_log(self, path_to_imu_log):
        
        df = self.read_IMU_csv(path_to_imu_log)

        df = df.rename(columns={'Record Time:': 'datetime', 
                        'AngleX：': 'roll', 
                        'AngleY：': 'pitch', 
                        'AngleZ：': 'yaw'})

        df['datetime'] = pd.DatetimeIndex(df['datetime']).tz_localize(pytz.timezone(self.FROM_TZ))
        df['datetime'] = pd.DatetimeIndex(df['datetime']).tz_convert(pytz.timezone(self.TO_TZ))

        df = df.groupby(df['datetime']).mean()

        df['tilt'] = [pu.get_tilt(pitch, roll, yaw)[0] for (pitch, roll, yaw) in zip(df['pitch'], df['roll'], df['yaw'])]
        
        df['tilt_dir'] = [pu.get_tilt(pitch, roll, yaw)[1] for (pitch, roll, yaw) in zip(df['pitch'], df['roll'], df['yaw'])]
    
        return df
    
    
    def read_Meteon_xlsx(self, path_to_meteon_xlsx):
        
        return pd.read_excel(path_to_meteon_xlsx, usecols=[0,2,5], skiprows=9, 
                                  names = ['Time', 'incoming (W/m^2)', 'reflected (W/m^2)'], parse_dates=True,
                                  sheet_name = None)
       
    def prep_Meteon_log(self, path_to_meteon_log):
        
        df = self.read_Meteon_xlsx(path_to_meteon_log)        
        
        for key in df:
  
            df[key]['Time'] = pd.DatetimeIndex(df[key]['Time']).tz_localize(None)

            df[key]['Time'] = pd.DatetimeIndex(df[key]['Time']).tz_localize(pytz.timezone(self.FROM_TZ))

            df[key]['Time'] = pd.DatetimeIndex(df[key]['Time']).tz_convert(pytz.timezone(self.TO_TZ))

            
            df[key]['albedo'] = df[key]['reflected (W/m^2)'] / df[key]['incoming (W/m^2)']
            
            df[key].set_index('Time', inplace=True)
        
        return df    
    
    
    def merge_logs(self, imu_log, meteon_log):
        
        keys_to_remove = []
        for key in meteon_log:
            
            meteon_log[key] = pd.concat([meteon_log[key], imu_log], axis=1, join='inner')
            
            if len(meteon_log[key]) == 0:
                    keys_to_remove.append(key)
        
        for k in keys_to_remove:
            meteon_log.pop(k)
        
        return meteon_log
    
    
    def read_gps_data(self, path_to_gps_log):
        
        df = pd.read_csv(path_to_gps_log, index_col=0)

        df['collection start'] = pd.DatetimeIndex(df['collection start'])
        
        return df
    
    
    def append_gps_data(self, gps_log, merged_log):
        
        for key in merged_log:
            
            avg_datetime = merged_log[key].index.mean()
            #avg_datetime = merged_log[key][-1:].index
            
            timediff = 0
            min_timediff = 100000000000
            gps_row = ''
            
            for index, row in gps_log.iterrows():
                
                timediff = np.abs((avg_datetime - row['collection start']).total_seconds())
                
                
                if timediff<min_timediff:
                    
                    min_timediff = timediff
                    gps_row = row
            
            merged_log[key]['lat'] = [gps_row['latitude']] * len(merged_log[key])
            merged_log[key]['lon'] = [gps_row['longitude']] * len(merged_log[key])
            merged_log[key]['alt_msl'] = [gps_row['elevation']] * len(merged_log[key])
                    
        return merged_log
    
    def add_UTM_coordinates(self, merged_log):
        
        for key in merged_log:
            
            projected_lon, projected_lat = process_util.convert_coordinates(self.source_epsg, self.dest_epsg, merged_log[key]['lon'], merged_log[key]['lat'])
        
            merged_log[key]['lon_utm'] = projected_lon
            merged_log[key]['lat_utm'] = projected_lat
        
        return merged_log
    
        
        
    def add_radiative_transfer_fields(self, merged_log):
        for key in merged_log:
            
            merged_log[key]['6s_Direct_Irradiance_Proportion'] = np.zeros(merged_log[key].shape[0])
            merged_log[key]['6s_Diffuse_Irradiance_Proportion'] = np.zeros(merged_log[key].shape[0])
            merged_log[key]['6s_Solar_Zenith_Angle'] = np.zeros(merged_log[key].shape[0])
            merged_log[key]['6s_Solar_Azimuth_Angle'] = np.zeros(merged_log[key].shape[0])
            
            for index, row in merged_log[key].iterrows():
                
                lat = row['lat']
                lon = row['lon']
                alt_m = row['alt_msl']
                dt = index
                
                p_dir, p_diff, solar_zenith, solar_azimuth = process_util.run_radiative_transfer(self.spectral_bandwidth, lat, lon, alt_m, dt)
                
                merged_log[key].loc[index, '6s_Direct_Irradiance_Proportion'] = p_dir
                merged_log[key].loc[index, '6s_Diffuse_Irradiance_Proportion'] = p_diff
                merged_log[key].loc[index, '6s_Solar_Zenith_Angle'] = solar_zenith
                merged_log[key].loc[index, '6s_Solar_Azimuth_Angle'] = solar_azimuth
        
        return merged_log
    
    def log_to_excel(self, path_to_output_xls):
        
        writer = pd.ExcelWriter(path_to_output_xls, engine='xlsxwriter')
        
        for key in self.merged_log:
            self.merged_log[key].index = pd.DatetimeIndex(self.merged_log[key].index).tz_localize(None)
            self.merged_log[key].to_excel(writer, sheet_name=key)
            
        writer.save()
        
        
    
    
        
  
    
    

