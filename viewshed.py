# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 17:35:19 2021

@author: x51b783
"""

import topo_correction_util as tcu
import numpy as np
import os
os.environ['PROJ_LIB'] = 'C:\\Users\\x51b783\\.conda\\envs\\gdal\\Library\\share\\proj'
os.environ['GDAL_DATA'] = 'C:\\Users\\x51b783\\.conda\\envs\gdal\\Library\\share'
from osgeo import gdal, gdalconst
from matplotlib import pyplot as plt


coarse_path = 'C:/Temp/3DEP/3DEP_clipped_UTM.tif'
model_path = 'C:/Temp/0311/sfm/elevation/elevation.tif'

coarse_source = gdal.Open(coarse_path, gdalconst.GA_ReadOnly)
model_source = gdal.Open(model_path, gdalconst.GA_ReadOnly)


driver = gdal.GetDriverByName("GTiff")
options = None
#x_loc = 462680
#y_loc = 5009017

x_loc = 462658.882742998
y_loc = 5008808.374467916

out = tcu.resample(model_source, coarse_source, 'C:/Temp/temp/viewshed_resampled.tif')

resampled_source = gdal.Open('C:/Temp/temp/viewshed_resampled.tif', gdalconst.GA_ReadOnly)
resampled_band = resampled_source.GetRasterBand(1)
resampled_band.SetNoDataValue(np.nan)

viewshed = gdal.ViewshedGenerate(resampled_band, 'GTiff', 
                                 'C:/Temp/temp/viewshed_coarse_temp.tif',
                                 creationOptions=options,
                                 observerX=x_loc, 
                                 observerY=y_loc, 
                                 observerHeight=1.5, 
                                 targetHeight = 0,
                                 visibleVal=1,
                                 invisibleVal=0,
                                 outOfRangeVal=0,
                                 noDataVal=0,
                                 dfCurvCoeff=0,
                                 mode=1,
                                 maxDistance=800)

viewshed_arr = viewshed.ReadAsArray()
plt.imshow(viewshed_arr)

viewshed_aligned = tcu.resample(viewshed,model_source,'C:/Temp/temp/viewshed_temp.tif')

viewshed_aligned=None
viewshed=None
model_source=None
model_band=None
model_proj=None
coarse_source=None
coarse_band=None
coarse_proj=None
resampled_source=None
resampled_band=None
out=None


