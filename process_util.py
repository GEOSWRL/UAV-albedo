# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 16:20:22 2021

@author: x51b783
"""

import pyproj
from Py6S import *

def convert_coordinates(source_epsg, dest_epsg,lon, lat):
    
    source_CRS=pyproj.CRS(source_epsg)
    dest_CRS=pyproj.CRS(dest_epsg) 

    lon, lat = pyproj.transform(source_CRS, dest_CRS, lat, lon)
    
    return lon, lat

def run_radiative_transfer(spectral_bandwidth, lat, lon, alt_m, dt):
    
    #.31, 2.7 for PR1 pyranometers
    bandwidth = spectral_bandwidth[1]-spectral_bandwidth[0]
    
    alt_km = alt_m/1000
    dt = str(dt)
    
    #initiate 6s
    s = SixS()
    
    #set 6s parameters
    s.wavelength = Wavelength(spectral_bandwidth[0], spectral_bandwidth[1])
    s.altitudes.set_target_custom_altitude(alt_km)
    s.geometry.from_time_and_location(lat, lon, dt, 0, 0)
    s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Continental)
    s.atmos_profile = AtmosProfile.FromLatitudeAndDate(lat, dt)

    #run 6s
    s.run()

    #get radiative transfer outputs
    p_dir = (s.outputs.percent_direct_solar_irradiance) #direct proportion of irradiance
    p_diff = 1-p_dir #diffuse proportion of irradiance
    solar_zenith = (s.outputs.solar_z)
    solar_azimuth = (s.outputs.solar_a)  
    
    return p_dir, p_diff, solar_zenith, solar_azimuth

        
