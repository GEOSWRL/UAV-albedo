# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 14:50:13 2020

@author: Andrew Mullen


conda install -c conda-forge earthpy
"""

import pandas as pd
import pytz
import os
#import earthpy as ep

#set working directory
#wd_path = os.path.join(ep.io.HOME, 'Documents', 'Mirror', 'SnowAlbedoProcessingChain', 'working_directory')
wd_path = 'C:/Users/x51b783/Desktop/temp_data_storage/YC20210428/'
if not (os.path.exists(wd_path)):
    print('working directory does not exist')

#set paths to logfiles    
#paths_to_DJI = [os.path.join(wd_path,'logfiles', 'dji', f) for f in os.listdir(os.path.join(wd_path, 'logfiles', 'dji'))]
paths_to_DJI = ['C:/Users/x51b783/Desktop/temp_data_storage/YC20210428/dji/csv/' + f for f in os.listdir('C:/Users/x51b783/Desktop/temp_data_storage/YC20210428/dji/csv/')]

#path_to_Meteon = os.path.join(wd_path, 'logfiles', 'meteon', os.listdir(os.path.join(wd_path, 'logfiles', 'meteon'))[0])
path_to_Meteon = 'C:/Users/x51b783/Desktop/temp_data_storage/YC20210428/meteon/YC20210428_pyranometers_csv.csv'


angle_tolerance = 5 #degree threshold of tilt and roll, angles greater than this will be filtered out
height_tolerance = 0.3 #records below this relative altitude(m) will be filtered out

timezone = 'US/Mountain'



def tilt_direction_to_azimuth(a):
    """
    Creates new Geotiff from numpy array

    Parameters
    ----------
    a : integer angle from -180 to 180 degrees
    
    Returns
    -------
    a : angle corrected to 360 degree azimuth (clockwise from 0 degrees at North)

    """
    
    if(a<0):
        a+=360
        return a
    return a

def parse_DJI(paths_to_DJI):
    """
    Creates new flight log file that is filtered, timestamps converted, and ready to be merged with irradiance data

    Parameters
    ----------
    path_to_DJI : string
        path to the directory containing DJI logfiles (in .csv format)
    
    Returns
    -------
    dfs : list of Pandas Dataframes
        DataFrames for filetered DJI flight logs file ready to be merged
    
    filenames : String
        Filenames corresponding to DJI flight logs

    """
    dfs = []
    
    for path in (paths_to_DJI):
        
        #extract desired columns
        df = pd.read_csv(path, usecols=['GPS:dateTimeStamp', 'IMU_ATTI(0):roll:C', 'IMU_ATTI(0):pitch:C', 'IMU_ATTI(0):yaw:C', 'IMU_ATTI(0):velComposite:C', 'IMU_ATTI(0):tiltInclination:C', 'IMU_ATTI(0):tiltDirectionEarthFrame:C', 'IMU_ATTI(0):tiltDirectionBodyFrame:C', 'GPS:Long', 'GPS:Lat', 'GPS:heightMSL', 'GPS:dateTimeStamp'], header=0)

        #filtering out altitudes <5m and pitch and roll >5 degrees
        #df = df.loc[(df['General:relativeHeight']>=height_tolerance) & (df['IMU_ATTI(0):roll']<=angle_tolerance) & (df['IMU_ATTI(0):roll']>=-angle_tolerance) & (df['IMU_ATTI(0):pitch']<=angle_tolerance) & (df['IMU_ATTI(0):pitch']>=-angle_tolerance)]

        #convert to mountain time
        df['GPS:dateTimeStamp'] = pd.DatetimeIndex(df['GPS:dateTimeStamp']).tz_localize(None)
        df['GPS:dateTimeStamp'] = pd.DatetimeIndex(df['GPS:dateTimeStamp']).tz_localize('Zulu')
        df['GPS:dateTimeStamp'] = pd.DatetimeIndex(df['GPS:dateTimeStamp']).tz_convert(pytz.timezone(timezone))
    
        #flight logs collect on milliseconds, so we must average values over each second
        df = df.groupby(df['GPS:dateTimeStamp']).mean()
        
        #adjust tilt_Direction to 360 deg. azimuth
        df['IMU_ATTI(0):tiltDirectionBodyFrame:C'] = df['IMU_ATTI(0):tiltDirectionBodyFrame:C'].apply(tilt_direction_to_azimuth)
        df['IMU_ATTI(0):tiltDirectionEarthFrame:C'] = df['IMU_ATTI(0):tiltDirectionEarthFrame:C'].apply(tilt_direction_to_azimuth)
        dfs.append(df)
        
        
    filenames = [f for f in os.listdir(os.path.join(wd_path, 'dji', 'csv'))]
        
    return dfs, filenames
    

def parse_Meteon(path_to_Meteon):
    """
    Creates new logfile with unnecesary columns removed, ready to be merged with DJI flight log

    Parameters
    ----------
    path_to_DJI : string
        path to the directory containing Meteon logfiles (in .csv format)
    
    Returns
    -------
    result : Pandas Dataframe
        filetered Meteon log file ready to be merged

    """    
    df = pd.read_csv(path_to_Meteon, usecols=[0,2,5], skiprows=9, names = ["Time", "incoming (W/m^2)", "reflected (W/m^2)"], parse_dates=True)
    #df = pd.read_csv(path_to_Meteon, usecols=[0,5,2], skiprows=9, names = ["Time", "reflected (W/m^2)", "incoming (W/m^2)"], parse_dates=True)
    
    #correct downward faceing sensor for leg interference
    reflected_corr = df['reflected (W/m^2)'].multiply(1.0197)
    df.insert(3,'albedo', reflected_corr.div(df['incoming (W/m^2)'])) #calculate albedo
    
    #df = df.loc[(df['albedo']<=1)] #albedo cannot be > 1
    
    df['Time'] = pd.DatetimeIndex(df['Time']).tz_localize(pytz.timezone(timezone))
    df.set_index('Time', inplace=True)
    return df
    

def merge_tables(DJI_parsed, Meteon_parsed):
    """
    Creates a new .csv file from merging the DJI flight log and Meteon data based on timestamp

    Parameters
    ----------
    DJI_parsed : string
        path to the directory containing parsed DJI logfile
    Meteon_parsed : string
        path to the directory containing parsed Meteon ligfile

    Returns
    -------
    merged: list of Pandas DataFrame objects
        DataFrame objects for each merged DJI flight log
        
    result : writes file in same directory as other files
        filtered and merged table containing all irradiance measurements with associated flight log

    """
    
    
    merged = []
    x=0
    for dji in DJI_parsed[0]:
        
        #take intersection of two dataframes based on index
        m = pd.concat([dji, Meteon_parsed], axis=1, join='inner')
        
        #add to list of dataframes
        merged.append(m)
        
        #save to csv
        m.to_csv(wd_path + 'merged/' + DJI_parsed[1][x][:-4] + "_merged.csv")
        
        x+=1
        
        
    return merged


DJI_parsed = parse_DJI(paths_to_DJI)
Meteon_parsed = parse_Meteon(path_to_Meteon)
merged = merge_tables(DJI_parsed, Meteon_parsed)

    
