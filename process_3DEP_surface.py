# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 11:43:50 2021

@author: x51b783
"""

from osgeo import gdal, gdalconst

class USGS_Surface_Data:
    
    PATH_TO_RAW_USGS_DEM = ''
    PATH_TO_RAW_USGS_SLOPE = ''
    PATH_TO_RAW_USGS_ASPECT = ''
    PATH_TO_RAW_LS8 = ''

    PATH_TO_PROCESSED_USGS_DEM = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/01_surface_data/3DEP/elevation/'
    PATH_TO_PROCESSED_USGS_SLOPE = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/01_surface_data/3DEP/slope/'
    PATH_TO_PROCESSED_USGS_ASPECT = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/01_surface_data/3DEP/aspect/'
    PATH_TO_PROCESSED_USGS_LS8 = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/01_surface_data/3DEP/LS8/'
    PATH_TO_USGS_COORDINATE_ARRAY = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/01_surface_data/3DEP/coordinates/'
    
    elevation_wgs = ''
    slope_wgs = ''
    aspect_wgs = ''
    ls8_wgs = ''
    
    elevation_utm = ''
    slope_utm = ''
    aspect_utm = ''
    ls8_utm = ''
    xcoords_utm = ''
    ycoords_utm = ''
    
    
    # init method or constructor
    def __init__(self, elevation_filename, slope_filename, aspect_filename, ls8_filename, xcoords_filename, ycoords_filename):
        
        try:
            
            self.elevation_utm = gdal.Open(self.PATH_TO_PROCESSED_USGS_DEM+elevation_filename, gdalconst.GA_ReadOnly)
            self.slope_utm = gdal.Open(self.PATH_TO_PROCESSED_USGS_SLOPE+slope_filename, gdalconst.GA_ReadOnly)
            self.aspect_utm = gdal.Open(self.PATH_TO_PROCESSED_USGS_ASPECT+aspect_filename, gdalconst.GA_ReadOnly)
            self.xcoords_utm = gdal.Open(self.PATH_TO_USGS_COORDINATE_ARRAY+xcoords_filename, gdalconst.GA_ReadOnly)
            self.ycoords_utm = gdal.Open(self.PATH_TO_USGS_COORDINATE_ARRAY+ycoords_filename, gdalconst.GA_ReadOnly)
            
        except:
            
            #not yet implemented
            self.elevation_wgs = gdal.Open(self.PATH_TO_RAW_USGS_DEM+elevation_filename, gdalconst.GA_ReadOnly)
            self.slope_wgs = gdal.Open(self.PATH_TO_RAW_USGS_SLOPE+slope_filename, gdalconst.GA_ReadOnly)
            self.aspect_wgs = gdal.Open(self.PATH_TO_RAW_USGS_ASPECT+aspect_filename, gdalconst.GA_ReadOnly)
  
        try:
            
            self.ls8_utm = gdal.Open(self.PATH_TO_PROCESSED_USGS_LS8+ls8_filename, gdalconst.GA_ReadOnly)
            
        except:
            
            #not yet implemented
            self.ls8_wgs = gdal.Open(self.PATH_TO_RAW_LS8+ls8_filename, gdalconst.GA_ReadOnly)
   
    def prep_surface_data(self):
        print('Hello, my name is', self.name)
        
    def fuse_data_sources(self):
        print('Hello, my name is', self.name)
        
    def get_elevation_array(self):
        
        return self.elevation_utm.GetRasterBand(1).ReadAsArray()
    
    def get_slope_array(self):
        
        return self.slope_utm.GetRasterBand(1).ReadAsArray()
    
    def get_aspect_array(self):
        
        return self.aspect_utm.GetRasterBand(1).ReadAsArray()
    
    def get_ls8_array(self):
        
        return self.ls8_utm.GetRasterBand(1).ReadAsArray()
    
    def get_xcoords_array(self):
        
        return self.xcoords_utm.GetRasterBand(1).ReadAsArray()
    
    def get_ycoords_array(self):
        
        return self.ycoords_utm.GetRasterBand(1).ReadAsArray()
    


    
