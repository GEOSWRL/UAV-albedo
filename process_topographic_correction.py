# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 16:15:33 2021

@author: x51b783
"""

import pandas as pd
import numpy as np
from osgeo import gdal, gdalconst
import process_util as pu
import math

class Topographic_Correction:
    
    output_filename = ''
    
    uav_data = ''
    surface_data = ''

    elevation_source_type = ''
    elev_array = ''
    slope_array = ''
    aspect_array = ''
    xcoords_array = ''
    ycoords_array = ''
    
    ls8_array = ''
    
    point_lon = ''
    point_lat = ''
    point_alt_msl = ''
    point_alt_agl = ''
    tilt = ''
    tilt_dir = ''
    
    pitch = ''
    roll = ''
    yaw = ''
    
    PFOV = ''
    PFOV_rad = ''
    
    uncorrected_albedo = ''
    corrected_albedo = ''
    
    solar_zenith = ''
    solar_azimuth = ''
    
    p_diffuse = ''
    p_direct = ''
    
    footprint = ''
    
    weighted_slope = ''
    weighted_aspect = ''
    weighted_ls8 = ''
    
    dist_x =''
    dist_y = ''
    elev_diff = ''
    
    
    def __init__(self, UAV_point, surface_data, elevation_source_type, PFOV, point_alt_agl = None, gps_point_on_ground = False):
        
        self.surface_data = surface_data
        self.elevation_source_type = elevation_source_type
        
        self.elev_array = self.surface_data.get_elevation_array()
        self.slope_array = self.surface_data.get_slope_array()
        self.aspect_array = self.surface_data.get_aspect_array()
        self.xcoords_array = self.surface_data.get_xcoords_array()
        self.ycoords_array = self.surface_data.get_ycoords_array()
        
        self.ls8_array = self.surface_data.get_ls8_array()
        
        self.uav_data = UAV_point
        self.point_lon = UAV_point['lon_utm']
        self.point_lat = UAV_point['lat_utm']
        self.tilt = UAV_point['tilt']
        self.tilt_dir = UAV_point['tilt_dir']
        self.point_alt_msl = UAV_point['alt_msl']
        
        self.pitch = UAV_point['pitch']
        self.roll = UAV_point['roll']
        self.yaw = UAV_point['yaw']
        
        self.uncorrected_albedo =  UAV_point['albedo']
        
        self.PFOV = PFOV
        self.PFOV_rad = np.radians(PFOV)
        
        if point_alt_agl == None:
            self.point_alt_agl = self.get_alt_agl()
            
        else:
            self.point_alt_agl = point_alt_agl
            
        if gps_point_on_ground:
            self.point_alt_msl += self.point_alt_agl
            
        self.solar_zenith = UAV_point['6s_Solar_Zenith_Angle']
        self.solar_azimuth = UAV_point['6s_Solar_Azimuth_Angle']
    
        self.p_diffuse = UAV_point['6s_Diffuse_Irradiance_Proportion']
        self.p_direct = UAV_point['6s_Direct_Irradiance_Proportion']
        

    def get_alt_agl(self):
        
        xcoord_dif = np.abs(np.subtract(self.xcoords_array[0], self.point_lon))
        ycoord_dif = np.abs(np.subtract(self.ycoords_array[:,0], self.point_lat))
        
        x_index = np.where(xcoord_dif == np.nanmin(xcoord_dif))[0][0]
        y_index = np.where(ycoord_dif == np.nanmin(ycoord_dif))[0][0]
        
        return self.point_alt_msl - self.elev_array[y_index][x_index]
        

    def run_viewshed(self, elev_band, point_lon, point_lat, agl_alt):
    
        viewshed = gdal.ViewshedGenerate(elev_band, 'GTiff', 
                                 'D:/UAV-albedo/data_test_dir/temp_files/temp_viewshed.tif',
                                 creationOptions=None,
                                 observerX=point_lon, 
                                 observerY=point_lat, 
                                 observerHeight = agl_alt, 
                                 targetHeight = 0,
                                 visibleVal=1,
                                 invisibleVal=0,
                                 outOfRangeVal=0,
                                 noDataVal=np.nan,
                                 dfCurvCoeff=1,
                                 mode=1,
                                 maxDistance=800)
        
        viewshed_resampled = pu.resample(viewshed, 
                                         self.surface_data.elevation_utm, 
                                         'D:/UAV-albedo/data_test_dir/temp_files/temp_viewshed_res.tif')
        
        viewshed_array = viewshed_resampled.GetRasterBand(1).ReadAsArray()
        
        return viewshed_array

    def calc_point_terrain_parameters(self):
    

        #create viewshed array
        viewshed_array = self.run_viewshed(self.surface_data.get_elevation_band(), self.point_lon, self.point_lat, self.point_alt_agl)
        
        #set elevation raster pixels to nan if outside viewshed
        not_visible = np.where(viewshed_array==0)
        
        self.elev_array[not_visible] = np.nan
    
        #calculate necesarry distance arrays for footprint projection
        self.elev_diff = self.point_alt_msl - self.elev_array # calculate elevation difference
        self.elev_diff[self.elev_diff<=0]=np.nan # points above the downward-facing sensor should be masked out as well
        self.dist_y = self.ycoords_array - self.point_lat
        self.dist_x = self.xcoords_array - self.point_lon
        
        #rotate the surface normal of the downward-facing sensor based off UAV pitch, roll, yaw
        surface_normal = [0,0,-1]
        pitch_radians = np.radians(self.pitch)
        roll_radians = np.radians(self.roll)
        yaw_radians = np.radians(self.yaw)
        surface_normal = pu.rotate_normals(surface_normal, pitch_radians, roll_radians, yaw_radians)
        
        #calculate incidence angle between radiating pixel and sensor
        angle = np.arcsin(np.abs((surface_normal[0] * self.dist_x + 
                                  surface_normal[1] * self.dist_y + 
                                  surface_normal[2] * -1 * self.elev_diff) /
                                 (np.sqrt(np.square(self.dist_x)+np.square(self.dist_y)+np.square(self.elev_diff)) *
                                  np.sqrt(np.square(surface_normal[0])+np.square(surface_normal[1])+np.square(surface_normal[2])
                                          ))
                                 ))
        
        #now filter pixels based on defined PFOV of sensor
        angle[angle<=(math.pi/2)-(self.PFOV_rad/2)]=np.nan
        self.footprint = angle
        
        #calculate weighting
        cosine_incidence = np.cos((math.pi/2)-angle)
        cos_sum = np.nansum(cosine_incidence)
        weighting = cosine_incidence/cos_sum  
        
        # calculate cosine wighted average of surface data
        weighted_aspect = pu.calc_weighted_avg(self.aspect_array, weighting)
        weighted_slope = pu.calc_weighted_avg(self.slope_array, weighting)
        weighted_ls8 = pu.calc_weighted_avg(self.ls8_array, weighting)
    
        return weighted_slope, weighted_aspect, weighted_ls8
    
    def topo_correction(self):
        
        self.weighted_slope, self.weighted_aspect, self.weighted_ls8 = self.calc_point_terrain_parameters()
        
        cos_pyranometer_incidence = pu.get_cos_incidence_angle(self.solar_zenith, self.tilt, self.tilt_dir, self.solar_azimuth)
        
        cos_slope_incidence = pu.get_cos_incidence_angle(self.solar_zenith, self.weighted_slope, self.weighted_aspect, self.solar_azimuth)
        
        corrected_albedo = self.uncorrected_albedo * ((self.p_diffuse * np.cos(np.radians(self.solar_zenith)) + self.p_direct * cos_pyranometer_incidence) / 
                                           (self.p_diffuse * np.cos(np.radians(self.solar_zenith)) + self.p_direct * cos_slope_incidence))
        
        self.corrected_albedo = corrected_albedo
        
        return

