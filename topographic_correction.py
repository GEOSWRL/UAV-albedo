# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 12:47:10 2021

@author: x51b783
"""

import os
import matplotlib.pyplot as plt
import numpy as np
#import geopandas
import pandas as pd
from osgeo import gdal, gdalconst, osr
import math
from mpl_toolkits.mplot3d import Axes3D
import pytz
from Py6S import *
import topo_correction_util as tcu
import angles
from scipy import ndimage
import pyproj
os.environ['PROJ_LIB'] = 'C:\\Users\\x51b783\\.conda\\envs\\gdal\\Library\\share\\proj'
os.environ['GDAL_DATA'] = 'C:\\Users\\x51b783\\.conda\\envs\gdal\\Library\\share'
################################################ Set Parameters ################################################

#path to DEM
coarse_elev_path = 'D:/field_data/YC/3DEP/3DEP_DEM_UTM.tif'

temp_elev = 'C:/Temp/temp_elev.tif'
usgs_slope = ''
usgs_aspect = ''
usgs_xcoords = ''
usgs_ycoords = ''
#Desired path to UTM projected DEM that is created in the "prep_rasters" function. Must end in '.tif'
elev_UTM_path = 'D:/field_data/YC/3DEP/3DEP_DEM_UTM.tif'

#Desired paths to slope and aspect rasters that are created in the "prep_rasters" function. Must end in '.tif'

path_to_slope = 'D:/field_data/YC/3DEP/3DEP_slope_UTM.tif'
path_to_aspect = 'D:/field_data/YC/3DEP/3DEP_aspect_UTM.tif'
path_to_coordinate_array_x = 'D:/field_data/YC/3DEP/3DEP_xcoords_UTM.tif'
path_to_coordinate_array_y = 'D:/field_data/YC/3DEP/3DEP_ycoords_UTM.tif'


#path to csv file
#csv file must contain latitude, longitude, altitude, pitch, roll, and yaw
csv_path = 'D:/field_data/YC/YC20210311/merged/albedo_10m_USGS.csv'

#FOV_path = 'D:/field_data/YC/YC20210311/merged/vertical_transects/vt1_FOV.csv'


#csv field names DJI
datetime_fname = 'datetime'
GPS_latitude_fname = 'GPS:Lat'
GPS_longitude_fname  = 'GPS:Long'
GPSAltitude_fname = 'GPS:heightMSL'
pitch_fname = 'IMU_ATTI(0):pitch:C'
roll_fname = 'IMU_ATTI(0):roll:C'
yaw_fname = 'IMU_ATTI(0):yaw:C'
tilt_fname = 'IMU_ATTI(0):tiltInclination:C'
tilt_dir_fname = 'IMU_ATTI(0):tiltDirectionEarthFrame:C'
albedo_meas_fname = 'albedo'
agl_alt_fname = 'agl_alt'

'''
#csv field names IMU
datetime_fname = 'datetime'
GPS_latitude_fname = 'latitude'
GPS_longitude_fname  = 'longitude'
GPSAltitude_fname = 'elevation'
pitch_fname = 'AngleY：'
roll_fname = 'AngleX：'
yaw_fname = 'AngleZ：'
tilt_fname = 'tilt'
tilt_dir_fname = 'tilt_dir'
albedo_meas_fname = 'albedo'
'''
source_epsg = 'EPSG:4326' #EPSG that the point data is initially stored in
dest_epsg = 'EPSG:32612' #UTM Zone 12-N

wgs_epsg = 4326
utm_epsg = 32612

#set sensor specifications
sensor_bandwidth = [0.31, 2.7] #in micrometers
sensor_half_FOV = 75 #in degrees
#sensor_FOVs = [30,32.5,35,37.5,40,42.5,45,47.5,50,52.5,55,57.5,60,62.5,65,67.5,70,72.5,75,77.5,80,82.5,85,87.5,89]
#sensor_FOVs = [30,35,40,45,50,55,60,65,70,75,80,85,89]
#sensor_FOVs = [30,70]
#sensor_FOVs = [80]
sensor_half_FOV_rad = np.radians(sensor_half_FOV)
#sensor_half_FOVs_rad = np.radians(sensor_FOVs)
geotransform = []

ss_elev = gdal.Open(elev_UTM_path, gdal.GA_ReadOnly)
geotransform = ss_elev.GetGeoTransform()

ss_elev = None

#enable or disable specific processes
prepare_rasters = False

prepare_point_data = True
run_radiative_transfer = True
calculate_terrain_parameters = True
run_topo_correction = True


#open up landsat 8 file and read as array
ls8 = gdal.Open('D:/field_data/YC/3DEP/ls8/YC20210311_ls8_3DEP.tif', gdal.GA_ReadOnly)
#ls8 = gdal.Open('D:/field_data/YC/3DEP/ls8/YC20210318_ls8_3DEP.tif', gdal.GA_ReadOnly)
#ls8 = gdal.Open('D:/field_data/YC/3DEP/ls8/YC20210428_ls8_3DEP.tif', gdal.GA_ReadOnly)
ls8_array = tcu.get_band_array(ls8)
ls8 = None


################################################### Code Body ##################################################

def radiative_transfer(gdf, row, index):
    print('running 6s radiative transfer')
    #.31, 2.7 for PR1 pyranometers
    bandwidth = sensor_bandwidth[1]-sensor_bandwidth[0]
    
    #print("running 6s radiative transfer for measurement taken at " + str(index))
    #gather row data from flight log entry
    lat = row[GPS_latitude_fname]
    lon = row[GPS_longitude_fname]
    alt_km = row[GPSAltitude_fname]/1000
    dt = str(index)
        
    #initiate 6s
    s = SixS()
    
    #set 6s parameters
    s.wavelength = Wavelength(sensor_bandwidth[0], sensor_bandwidth[1])
    s.altitudes.set_target_custom_altitude(alt_km)
    s.geometry.from_time_and_location(lat, lon, dt, 0, 0)
    s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Continental)
    #s.atmos_profile = AtmosProfile.FromLatitudeAndDate(lat, dt)
    s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeWinter)
    #s.visibility = None
    #s.aot550 = 0.1
    
    #run 6s
    s.run()
    print('hi')
    #get radiative transfer outputs
    
    print(s.outputs)
    global_irradiance = (s.outputs.direct_solar_irradiance + s.outputs.diffuse_solar_irradiance + s.outputs.environmental_irradiance)*bandwidth
    p_dir = (s.outputs.percent_direct_solar_irradiance) #direct proportion of irradiance
    p_diff = 1-p_dir #diffuse proportion of irradiance
    solar_zenith = (s.outputs.solar_z)
    solar_azimuth = (s.outputs.solar_a)  
    print('6s_global: ' + str(global_irradiance))
    gdf.loc[index, '6s_modeled_global_irradiance'] = global_irradiance
    gdf.loc[index, '6s_Direct_Irradiance_Proportion'] = p_dir
    gdf.loc[index, '6s_Diffuse_Irradiance_Proportion'] = p_diff
    gdf.loc[index, '6s_Solar_Zenith_Angle'] = solar_zenith
    gdf.loc[index, '6s_Solar_Azimuth_Angle'] = solar_azimuth
        
    return gdf

def make_coordinate_array(geotransform, image_shape):
    print(geotransform)
    coordinate_array_x = np.zeros(image_shape)
    coordinate_array_y = np.zeros(image_shape)

    pixel_y = geotransform[3]
    
    pixel_x = geotransform[0]

    for row in range(0, image_shape[0]):
    
        pixel_x = geotransform[0]
        pixel_y += geotransform[5]
    
        for col in range(0, image_shape[1]):
            pixel_x += geotransform[1]
        
            coordinate_array_x[row][col] = pixel_x
            coordinate_array_y[row][col] = pixel_y
            
    tcu.write_geotiff(path_to_coordinate_array_x, image_shape, geotransform, 32612, coordinate_array_x)
    tcu.write_geotiff(path_to_coordinate_array_y, image_shape, geotransform, 32612, coordinate_array_y)
    
    return coordinate_array_x, coordinate_array_y
    
def prep_rasters():
    
    print('preparing raster data')
    
    #elev = gdal.Open(elev_path, gdal.GA_ReadOnly) # open GeoTiff in read only mode
    #warp = gdal.Warp(elev_UTM_path,elev,dstSRS = dest_epsg) # reproject elevation GeoTiff from WGS to UTM

    # close files
    #warp = None
    #elev = None
    
    elev_UTM = gdal.Open(elev_UTM_path, gdal.GA_ReadOnly) # open reprojected elevation GeoTiff 
    
    #use gdal DEM processing to create slope and aspect rasters
    #processing_options = gdal.DEMProcessingOptions(alg = 'ZevenbergenThorne', format = 'GTiff')
    #slope_UTM = gdal.DEMProcessing(path_to_slope, elev_UTM_path, 'slope')
    #aspect_UTM = gdal.DEMProcessing(path_to_aspect, elev_UTM_path, 'aspect')
    slope_UTM = gdal.Open(path_to_slope, gdal.GA_ReadOnly)
    aspect_UTM = gdal.Open(path_to_aspect, gdal.GA_ReadOnly)
    
    
    #represent the rasters as numpy arrays
    elev_array = tcu.get_band_array(elev_UTM)
    slope_array = tcu.get_band_array(slope_UTM)
    aspect_array = tcu.get_band_array(aspect_UTM)
    
    # the raster geotransform tells the precise x,y location of the upper left corner of the upper left pixel, as well as pixel size
    geotransform = elev_UTM.GetGeoTransform()
    image_shape = np.shape(elev_array)
    
    
    coordinate_array_x, coordinate_array_y = make_coordinate_array(geotransform, image_shape)
    
    
    elev_UTM = None
    slope_UTM = None
    aspect_UTM = None
    
    #return rasters as arrays
    return elev_array, slope_array, aspect_array, coordinate_array_x, coordinate_array_y

def convert_coordinates(lon, lat):
    # Define the Rijksdriehoek projection system (EPSG 28992)
    wgs84=pyproj.CRS(source_epsg) # LatLon with WGS84 datum used by GPS units and Google Earth 
    utm_12N=pyproj.CRS(dest_epsg) # UK Ordnance Survey, 1936 datum 

    lon, lat = pyproj.transform(wgs84, utm_12N, lat, lon)
    
    return lon, lat

def prep_point_data():
    
    print('preparing point data')
    
    gdf = pd.read_csv(csv_path, parse_dates = True, index_col = datetime_fname)
    
    if gdf.index.tzinfo is None:
        gdf.index = gdf.index.tz_localize('US/Mountain')
        
    gdf.index = gdf.index.tz_convert(pytz.timezone('gmt'))
    
    
    #df = run_radiative_transfer(row)
    projected_lon, projected_lat = convert_coordinates(gdf[GPS_longitude_fname], gdf[GPS_latitude_fname])
    gdf['lon_utm'] = projected_lon
    gdf['lat_utm'] = projected_lat
    

    gdf['pitch_radians'] = np.radians(gdf[pitch_fname])
    gdf['roll_radians'] = np.radians(gdf[roll_fname])
    gdf['yaw_radians'] = np.radians(gdf[yaw_fname])

    if(calculate_terrain_parameters==True):
        gdf['mean_slope'] = np.zeros(gdf.shape[0])
        #gdf['mean_aspect'] = np.zeros(gdf.shape[0])
        
        gdf['cos_avg_slope_ss'] = np.zeros(gdf.shape[0])
        gdf['cos_avg_aspect_ss'] = np.zeros(gdf.shape[0])
        
        '''
        gdf['cos_avg_slope_bg'] = np.zeros(gdf.shape[0])
        gdf['cos_avg_aspect_bg'] = np.zeros(gdf.shape[0])
        gdf['cos_avg_slope_usgs'] = np.zeros(gdf.shape[0])
        gdf['cos_avg_aspect_usgs'] = np.zeros(gdf.shape[0])
        '''
    #create new dataframe columns from radiative transfer storage arrays
    if(run_radiative_transfer==True):
        gdf['6s_Direct_Irradiance_Proportion'] = np.zeros(gdf.shape[0])
        gdf['6s_Diffuse_Irradiance_Proportion'] = np.zeros(gdf.shape[0])
        gdf['6s_Solar_Zenith_Angle'] = np.zeros(gdf.shape[0])
        gdf['6s_Solar_Azimuth_Angle'] = np.zeros(gdf.shape[0])
        gdf['6s_modeled_global_irradiance'] = np.zeros(gdf.shape[0])
        
    if(run_topo_correction):
        gdf['corrected_albedo_ss'] = np.zeros(gdf.shape[0]) #cosine corrected
        gdf['cos_avg_ls8_ss'] = np.zeros(gdf.shape[0])
        #gdf['arithmetic_avg_corrected_albedo'] = np.zeros(gdf.shape[0])
        
        '''
        gdf['corrected_albedo_bg'] = np.zeros(gdf.shape[0]) #cosine corrected
        gdf['cos_avg_ls8_bg'] = np.zeros(gdf.shape[0])
        
        gdf['corrected_albedo_usgs'] = np.zeros(gdf.shape[0]) #cosine corrected
        gdf['cos_avg_ls8_usgs'] = np.zeros(gdf.shape[0])
        '''
        
        #gdf['sensor_incidence_angle'] = np.zeros(gdf.shape[0])
        #gdf['slope_incidence_angle'] = np.zeros(gdf.shape[0])
    
    
    
    return gdf
    
def run_viewshed(elev_band, point_lon, point_lat, agl_alt=10):
    
    viewshed = gdal.ViewshedGenerate(elev_band, 'GTiff', 
                                 'C:/Temp/3DEP/viewshed_test.tif',
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

    #viewshed_arr = viewshed.ReadAsArray()
    #plt.imshow(viewshed_arr)
    #viewshed = None
    
    return viewshed

def reduce_array_extent(array, geotransform):
    ulx = geotransform[0]
    uly = geotransform[3]
    
    xres = geotransform[1]
    yres = geotransform[5]

    #return indices of non_null pixels
    arr_non_null= np.argwhere(array>0)

    #split in to 2 arrays of y coords, xcoords
    coords = np.hsplit(arr_non_null,2)
    
    #find max and min coordinates to form new bounds
    ymax=np.max(coords[0])
    ymin=np.min(coords[0])

    xmax=np.max(coords[1])
    xmin=np.min(coords[1])

    clipped_arr = array[ymin:ymax+1, xmin:xmax+1]

    new_ulx = ulx + xres*xmin
    new_uly = uly + yres*ymin
    
    new_geotransform = [new_ulx, xres, 0, new_uly, 0, yres]
    
    return clipped_arr, new_geotransform

def calc_terrain_parameters(elev_array, slope_array, aspect_array, coordinate_array_x, coordinate_array_y, gdf, row, index, model_source, coarse_source):
    
    print('calculating terrain parameters')
        
    #point_lon = row['geometry'].centroid.x # centroid.x is x coordinate of point geometry feature in UTM
    #point_lat = row['geometry'].centroid.y # centroid.y is y coordinate of point geometry feature in UTM
    point_lon = row['lon_utm']
    point_lat = row['lat_utm']
    #print(point_lon, point_lat)
    point_elev = row[GPSAltitude_fname]
    
    ################### create viewshed array ###############################
    
    resampled = tcu.resample(model_source, coarse_source, 'C:/Temp/temp/viewshed_resampled.tif')
    resampled_band = resampled.GetRasterBand(1)
    resampled_band.SetNoDataValue(np.nan)
    
    #viewshed = run_viewshed(resampled_band, point_lon, point_lat, row['agl_alt'])
    viewshed = run_viewshed(resampled_band, point_lon, point_lat)
    
    #resample viewshed array to original resolution
    viewshed_aligned = tcu.resample(viewshed, model_source,'C:/Temp/temp/viewshed_temp.tif')
    viewshed_array = viewshed_aligned.GetRasterBand(1).ReadAsArray()
    
    not_visible = np.where(viewshed_array==0)
    elev_array[not_visible] = np.nan
    
    
    
    #################### create footprint projection ###########################
    elev_diff = point_elev - elev_array # calculate elevation difference
    elev_diff[elev_diff<=0]=np.nan # points above the downward-facing sensor should be masked out as well
    
    
    #print(np.nanmax(elev_diff))
    #print(np.nanmin(elev_diff))

    # now that we have both coordinate arrays, we can turn them into distance arrays by subtracting the pixel coordinates from the 
    # coordinates of the measurement point. Since everything is in UTM this distance is in meters.

    dist_y = coordinate_array_y - point_lat
    #tcu.write_geotiff('C:/Temp/IMU/distx.tif', np.shape(dist_x), geotransform, 32612, dist_x)
    
    dist_x = coordinate_array_x - point_lon
    
    #print(np.nanmax(dist_x))
    #print(np.nanmin(dist_x))
    #print(np.nanmax(dist_y))
    #print(np.nanmin(dist_y))
    #notice that x and y are switched here. This is because we need the coordinate system to be in the form of 
    #North = x axis, East = y axis, Up/down = z axis

    surface_normal = [0,0,-1]
    
    pitch = row['pitch_radians']
    roll = row['roll_radians']
    yaw = row['yaw_radians']

    '''
    rot_matrix = [
        [np.cos(yaw)*np.cos(pitch), np.cos(yaw)*np.sin(roll)*np.sin(pitch)-np.cos(roll)*np.sin(yaw), np.sin(roll)*np.sin(yaw)+np.cos(roll)*np.cos(yaw)*np.sin(pitch)],
        [np.cos(pitch)*np.sin(yaw), np.cos(roll)*np.cos(yaw)+np.sin(roll)*np.sin(yaw)*np.sin(pitch), np.cos(roll)*np.sin(yaw)*np.sin(pitch)-np.cos(yaw)*np.sin(roll)],
        [-1*np.sin(pitch), np.cos(pitch)*np.sin(roll), np.cos(roll)*np.cos(pitch)],]
    
    surface_normal = np.dot(rot_matrix, surface_normal)
    '''
    surface_normal = angles.rotate_normals(surface_normal, pitch, roll, yaw)
    
    
    #calculate incidence angle between radiating pixel and sensor
    angle = np.arcsin(np.abs((surface_normal[0] * dist_x + 
                              surface_normal[1] * dist_y + 
                              surface_normal[2] * -1 * elev_diff) /
                             (np.sqrt(np.square(dist_x)+np.square(dist_y)+np.square(elev_diff)) *
                              np.sqrt(np.square(surface_normal[0])+np.square(surface_normal[1])+np.square(surface_normal[2])
                                      ))
                             ))
    
    
    #plt.imshow(np.degrees(angle))
    #tcu.write_geotiff('C:/Temp/angle.tif', np.shape(angle), geotransform, utm_epsg, np.degrees(angle))
    
    #filter pixels based on FOV of sensor
    
    angle[angle<=(math.pi/2)-sensor_half_FOV_rad]=np.nan
    #tcu.write_geotiff('D:/field_data/YC/YC20210428/imu/test_angle_80.tif', np.shape(angle), geotransform, utm_epsg, np.degrees(angle))
    #nan_indices = np.where(np.isnan(angle))
    #print('max angle: ' + str(90-np.degrees(np.nanmin(angle))))
    #set pixels to nan in other arrays
    #elev_array[nan_indices] = np.nan
    
    #plt.imshow(elev_array)
    #note that the maximum angle should never greater than 90 degrees (1.5708 rad)
    #and the minimum angle should never be less than 90-HFOV (.349066 rad for HFOV = 70 degrees)

    cosine_incidence = np.cos((math.pi/2)-angle)
    cos_sum = np.nansum(cosine_incidence)
    weighting = cosine_incidence/cos_sum

    
    # calculate cosine wighted average
    aspect_arr_weighted = weighting * aspect_array
    weighted_aspect = np.nansum(aspect_arr_weighted)
    print('cosine-weighted mean aspect: ' + str(weighted_aspect))
    
    
    #cos_avg_aspect = cos_avg_aspect.append(weighted_aspect)
    
    #print('aspect: ' + str(weighted_aspect))
    #print('tilt_dir: ' + str(row['tilt_dir']))
    
    
    # calculate cosine wighted average
    slope_arr_weighted = weighting * slope_array
    weighted_slope = np.nansum(slope_arr_weighted)
    #print('cosine-weighted mean slope: ' + str(weighted_slope))
    
    #cos_avg_slope = cos_avg_slope.append(weighted_slope)

    
    # now calculate arithmetic mean
    #aspect_arr_masked = aspect_arr_weighted/weighting
    #arth_mean_aspect = np.nanmean(aspect_arr_masked)
    #print('arithmetic mean aspect: ' + str(arth_mean_aspect))
    #gdf.loc[index, 'mean_aspect'] = arth_mean_aspect
    #weighted_aspect = arth_mean_aspect
    
    # now calculate arithmetic mean
    #slope_arr_masked = slope_arr_weighted/weighting
    #arth_mean_slope = np.nanmean(slope_arr_masked)
    #print('arithmetic mean slope: ' + str(arth_mean_slope))
    #mean_slope = mean_slope.append(arth_mean_slope)
    #weighted_slope = arth_mean_slope
    

    
    #calculate cosine averaged ls8 albedo value
    ls8_arr_weighted = weighting * ls8_array
    weighted_ls8 = np.nansum(ls8_arr_weighted)
    
    #ls8_arr_masked = ls8_arr_weighted/weighting
    #arth_mean_ls8 = np.nanmean(ls8_arr_masked)
    #print('cosine-weighted mean aspect: ' + str(weighted_aspect))
    gdf.loc[index, 'cos_avg_ls8_ss'] = weighted_ls8
    
    resampled = None
    resampled_band = None
    viewshed = None
    viewshed_aligned = None
    
    return weighted_slope, weighted_aspect

def topo_correction(gdf, row, index, slope_field, aspect_field):
    
    measured_albedo = row[albedo_meas_fname] 
    tilt = row[tilt_fname] 
    tilt_dir = row[tilt_dir_fname] 
    #tilt_dir = row['mean_aspect']
    #slope_mean = row['mean_slope'] 
    slope_cos = row[slope_field]
    #aspect_mean = row['mean_aspect'] 
    aspect_cos = row[aspect_field]
    solar_zenith = row['6s_Solar_Zenith_Angle']
    solar_azimuth = row['6s_Solar_Azimuth_Angle'] 
    p_dir = row['6s_Direct_Irradiance_Proportion'] 
    p_diff = row['6s_Diffuse_Irradiance_Proportion']
    
    #print('zenith_angle: ' + str(solar_zenith))
    solar_zenith_rad = math.radians(solar_zenith)
    
    cos_pyranometer_incidence = tcu.get_cos_incidence_angle(solar_zenith, tilt, tilt_dir, solar_azimuth)
    
    #print('pyranometer incidence angle: ' + str(math.degrees(math.acos(cos_pyranometer_incidence))))
    
    #cos_mean_slope_incidence = tcu.get_cos_incidence_angle(solar_zenith, slope_mean, aspect_mean, solar_azimuth)
    
    cos_cos_slope_incidence = tcu.get_cos_incidence_angle(solar_zenith, slope_cos, aspect_cos, solar_azimuth)
    
    #print('slope incidence angle: ' + str(math.degrees(math.acos(cos_slope_incidence))))
    
    #arithmetic_avg_corrected_albedo = measured_albedo * ((p_diff * np.cos(solar_zenith_rad) + p_dir * cos_pyranometer_incidence) / 
    #                                   (p_diff * np.cos(solar_zenith_rad) + p_dir * cos_mean_slope_incidence))
    
    cosine_avg_corrected_albedo = measured_albedo * ((p_diff * np.cos(solar_zenith_rad) + p_dir * cos_pyranometer_incidence) / 
                                       (p_diff * np.cos(solar_zenith_rad) + p_dir * cos_cos_slope_incidence))
    
    gdf.loc[index, 'cos_sensor_incidence_angle'] = cos_pyranometer_incidence
    gdf.loc[index, 'cos_slope_incidence_angle'] = cos_cos_slope_incidence
    
    #gdf.loc[index, 'arithmetic_avg_corrected_albedo'] = arithmetic_avg_corrected_albedo
    
    return cosine_avg_corrected_albedo

def process_handler():
    gdf = pd.DataFrame()
    elev_array = []
    slope_array = []
    aspect_array = []
    coordinate_array_x = []
    coordinate_array_y = []
    
    if prepare_rasters == False:
        print('loading rasters')
        ss_elev = gdal.Open(elev_UTM_path, gdal.GA_ReadOnly) # open reprojected elevation GeoTiff 
        ss_slope = gdal.Open(path_to_slope, gdal.GA_ReadOnly)
        ss_aspect = gdal.Open(path_to_aspect, gdal.GA_ReadOnly)
        ss_coordinate_x = gdal.Open(path_to_coordinate_array_x, gdal.GA_ReadOnly)
        ss_coordinate_y = gdal.Open(path_to_coordinate_array_y, gdal.GA_ReadOnly)
        
        coarse_elev = gdal.Open(coarse_elev_path, gdal.GA_ReadOnly)
        
    
        ss_elev_arr = tcu.get_band_array(ss_elev)
        ss_slope_arr = tcu.get_band_array(ss_slope)
        ss_aspect_arr = tcu.get_band_array(ss_aspect)
        ss_coordinate_array_x_arr = tcu.get_band_array(ss_coordinate_x)
        ss_coordinate_array_y_arr = tcu.get_band_array(ss_coordinate_y)

        print('rasters loaded')
        
        
    else:
        
        elev_array, slope_array, aspect_array, coordinate_array_x, coordinate_array_y = prep_rasters()
    print('prepping point data')  
    gdf = prep_point_data()
    print('point data prepped')  
    for index, row in gdf.iterrows():
        print('-----------------------Row-------------------------')
        print('measured incoming: ' + str(row['incoming (W/m^2)']))
        
        if calculate_terrain_parameters:
            ss_slope, ss_aspect = calc_terrain_parameters(ss_elev_arr, ss_slope_arr, ss_aspect_arr, ss_coordinate_array_x_arr, ss_coordinate_array_y_arr, gdf, row, index,
                                                          ss_elev, coarse_elev)
            gdf.loc[index, 'cos_avg_slope_ss'] = ss_slope
            gdf.loc[index, 'cos_avg_aspect_ss'] = ss_aspect
            
            
            
        if run_radiative_transfer:
            gdf = radiative_transfer(gdf, row, index)
        
    if run_topo_correction:
        print('running topographic correction')
        
        for index, row in gdf.iterrows(): 
            cosine_avg_corrected_albedo_ss = topo_correction(gdf, row, index, 'cos_avg_slope_ss', 'cos_avg_aspect_ss')
            gdf.loc[index, 'corrected_albedo_ss'] = cosine_avg_corrected_albedo_ss
        
        
    ss_elev = None 
    ss_slope = None
    ss_aspect = None
    ss_coordinate_x = None
    ss_coordinate_y = None 
    
    gdf.to_csv(csv_path)
    
    return gdf
    '''
    return(gdf['albedo'].to_numpy(), gdf['corrected_albedo_ss'].to_numpy(), 
           gdf['cos_avg_ls8_ss'].to_numpy(), gdf['agl_alt'].to_numpy())
    '''
'''
df_fov = pd.DataFrame(columns = ['FOV', 'albedo', 'corrected_albedo', 'ls8_albedo', 'agl_alt'])

for fov in sensor_half_FOVs_rad:
    #print(np.degrees(fov))
    sensor_half_FOV_rad = fov
    uncor_albedo,cor_albedo,ls8_albedo, agl_alt = process_handler()

    #df_temp = pd.DataFrame({ 'FOV': [np.degrees(fov)], 'dif': [np.abs(uncor_albedo[0]-uncor_albedo[1])], 'cor_dif': [np.abs(cor_albedo[0]-uncor_albedo[1])]})
    df_temp = pd.DataFrame({ 'FOV': [np.degrees(fov)] * len(uncor_albedo), 'abedo': uncor_albedo, 
                            'corrected_albedo': cor_albedo, 'ls8_albedo': ls8_albedo, 'agl_alt': agl_alt})
    df_fov = df_fov.append(df_temp)
    

 
df_fov.to_csv(FOV_path) 
'''
  

def main():
    process_handler()  
    print('hi')

if __name__ == "__main__":
    #prep_rasters()
    main()
    print('hi')





