# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 16:20:22 2021

@author: x51b783
"""

import pyproj
from Py6S import *
from osgeo import gdal, gdalconst, osr
import numpy as np
import math
import os
from scipy.spatial.transform import Rotation as R

def convert_coordinates(source_epsg, dest_epsg,lon, lat):
    
    source_CRS=pyproj.CRS(source_epsg)
    dest_CRS=pyproj.CRS(dest_epsg) 

    lon, lat = pyproj.transform(source_CRS, dest_CRS, lat, lon)
    
    return lon, lat


def resample(original_source, desired_source, destination_path):

    original_proj = original_source.GetProjection()

    desired_gt = desired_source.GetGeoTransform()
    desired_proj = desired_source.GetProjection()
    desired_cols = desired_source.RasterXSize
    desired_rows = desired_source.RasterYSize
    
    minX = desired_gt[0]
    maxX = desired_gt[0] + (desired_cols * desired_gt[1])
    
    minY = desired_gt[3] + (desired_rows * desired_gt[5])
    maxY = desired_gt[3]

    warp_options = gdal.WarpOptions(format = 'GTiff', 
                                outputBounds = [minX, minY, maxX, maxY], 
                                width = desired_cols, height = desired_rows,
                                srcSRS = original_proj, dstSRS = desired_proj)
    
    out = gdal.Warp(destination_path, original_source, options = warp_options)
    
    return out


def make_coordinate_array(path_to_coordinate_array_x, path_to_coordinate_array_y, geotransform, image_shape, method = 'center'):
    
    coordinate_array_x = np.zeros(image_shape)
    coordinate_array_y = np.zeros(image_shape)
    
    pixel_y = geotransform[3]
    pixel_x = geotransform[0]
    
    if method == 'center':
        pixel_y += (geotransform[5]/2)
        pixel_x += (geotransform[1]/2)

    for row in range(0, image_shape[0]):
        for col in range(0, image_shape[1]):
            
            coordinate_array_x[row][col] = pixel_x
            coordinate_array_y[row][col] = pixel_y
            
            pixel_x += geotransform[1]
        
        pixel_x = geotransform[0]
        
        if method == 'center':
            pixel_x += (geotransform[1]/2)
               
        pixel_y += geotransform[5]  
        
        
    write_geotiff(path_to_coordinate_array_x, image_shape, geotransform, 32612, coordinate_array_x)
    write_geotiff(path_to_coordinate_array_y, image_shape, geotransform, 32612, coordinate_array_y)
    
    return coordinate_array_x, coordinate_array_y


def get_band_array(file):
    
    band = file.GetRasterBand(1) # get raster band
    ndv = band.GetNoDataValue() # get no data value
    
    
    array = band.ReadAsArray() # read in raster as an array
    
    array[array==ndv]=np.nan # set nan values to np.nan so they do not interfere with calculations
    
    return array


def write_geotiff(new_image_name, image_shape, geotransform, projection, dataset):
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(new_image_name, image_shape[1], image_shape[0], 1, gdalconst.GDT_Float32)
    
    outdata.SetGeoTransform(geotransform)   ##sets same geotransform as input
    srs = osr.SpatialReference()            # establish encoding
    srs.ImportFromEPSG(projection)                # WGS84 lat/long
    outdata.SetProjection(srs.ExportToWkt())
    #outdata.GetRasterBand(1).SetNoDataValue(ndv)
    outdata.GetRasterBand(1).WriteArray(dataset)
    
    #outdata.GetRasterBand(1).SetNoDataValue(10000)##if you want these values transparent
    outdata.FlushCache() ##saves to disk!!
    outdata = None

def calc_weighted_avg(array, weighting):
    
    return np.nansum(weighting * array)

def sin(angle):
    return math.sin(angle)


def cos(angle):
    return math.cos(angle)


def get_cos_incidence_angle(solar_zenith, slope, slope_orientation, solar_azimuth):
    
    solar_zenith = math.radians(solar_zenith)
    slope = math.radians(slope)
    aspect = math.radians(slope_orientation)
    solar_azimuth = math.radians(solar_azimuth)
    
    return  (sin(solar_zenith) * sin(slope) * cos(solar_azimuth-aspect) +
             cos(solar_zenith) * cos(slope))
    
def get_tilt_dir(surface_normal, pitch, roll, yaw):
    
    vector_north = [[1], [0], [0]]
    
    angle = np.arccos(np.abs((vector_north[0][0] * surface_normal[0][0] + 
                              vector_north[1][0] * surface_normal[1][0] + 
                              vector_north[2][0] * 0) /
                             (np.sqrt(np.square(surface_normal[0][0])+np.square(surface_normal[1][0])+np.square(0)) *
                              np.sqrt(np.square(vector_north[0][0])+np.square(vector_north[1][0])+np.square(vector_north[2][0])
                                      ))
                             ))
    
    tilt_dir_deg = np.degrees(angle)
    
    if(pitch >=0 and roll >=0):
        return 180-tilt_dir_deg
    
    if(pitch >=0 and roll <=0):
        return 180+tilt_dir_deg
    
    if(pitch <=0 and roll <=0):
        return 360-tilt_dir_deg
    
    return tilt_dir_deg

def get_tilt(pitch, roll, yaw):
    #pitch*=-1
    pitch = np.radians(pitch)
    roll = np.radians(roll)
    yaw = np.radians(yaw)

    surface_normal = [[0],[0],[1]]

    rot_matrix = [
            [np.cos(yaw)*np.cos(pitch), np.cos(pitch)*np.sin(yaw), -1*np.sin(pitch)],
            [np.cos(yaw)*np.sin(roll)*np.sin(pitch)-np.cos(roll)*np.sin(yaw), np.cos(roll)*np.cos(yaw)+np.sin(roll)*np.sin(yaw)*np.sin(pitch), np.cos(pitch)*np.sin(roll)],
            [np.sin(roll)*np.sin(yaw)+np.cos(roll)*np.cos(yaw)*np.sin(pitch), np.cos(roll)*np.sin(yaw)*np.sin(pitch)-np.cos(yaw)*np.sin(roll), np.cos(roll)*np.cos(pitch)],
            ]
    
    new_surface_normal = np.dot(rot_matrix, surface_normal)
        
    angle = np.arccos(np.abs((surface_normal[0][0] * new_surface_normal[0][0] + 
                              surface_normal[1][0] * new_surface_normal[1][0] + 
                              surface_normal[2][0] * new_surface_normal[2][0]) /
                             (np.sqrt(np.square(new_surface_normal[0][0])+np.square(new_surface_normal[1][0])+np.square(new_surface_normal[2][0])) *
                              np.sqrt(np.square(surface_normal[0][0])+np.square(surface_normal[1][0])+np.square(surface_normal[2][0])
                                      ))
                             ))
    tilt_deg = np.degrees(angle)
    tilt_dir_deg = get_tilt_dir(new_surface_normal, pitch, roll, yaw)
    
    return tilt_deg, tilt_dir_deg

def rotate_normals(surface_normal, pitch_rad, roll_rad, yaw_rad):

    r = R.from_euler('ZYX', [yaw_rad, pitch_rad, roll_rad], degrees=False)
    
    return r.apply(surface_normal)

def run_radiative_transfer(spectral_bandwidth, lat, lon, alt_m, dt):
    
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

        
