# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 12:29:24 2021

@author: x51b783
"""
import os
os.environ['PROJ_LIB'] = 'C:\\Users\\x51b783\\.conda\\envs\\gdal\\Library\\share\\proj'
os.environ['GDAL_DATA'] = 'C:\\Users\\x51b783\\.conda\\envs\gdal\\Library\\share'
from osgeo import gdal, gdalconst, osr
import numpy as np
import topo_correction_util as tcu
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

degree_sign = u"\N{DEGREE SIGN}"

'''
UTM_path = 'C:/Temp/3DEP/3DEP_DEM_UTM.tif'
im = gdal.Open(UTM_path, gdalconst.GA_ReadOnly)
gt = im.GetGeoTransform()
shape = np.shape(im.GetRasterBand(1).ReadAsArray())


tcu.make_coordinate_array('C:/Temp/3DEP/3DEP_xcoords.tif', 'C:/Temp/3DEP/3DEP_ycoords.tif', gt, shape, method = 'center')


im = None
shape = None
'''

'''
wgs_path = 'C:/Temp/bareground/elevation/YC20200805_DEM_1m_clipped.tif'
warp = gdal.Warp(UTM_path,wgs_path,dstSRS = 'EPSG:32612') # reproject elevation GeoTiff from WGS to UTM
'''
path = 'D:/field_data/YC/FOV_sensitivity/'

stats = pd.DataFrame(columns = ['PFOV (degrees)', 'Mean Absolute Error', 'Mean Absolute Error Corrected'])

for file in os.listdir(path):
    if file.endswith('.csv'):
        df = pd.read_csv(path+file)
        mean = df['dif'].mean()
        sd = df['dif'].std()
    
    
        normalized_df = pd.DataFrame({'PFOV (degrees)': df['FOV']*2, 'Mean Absolute Error': df['dif'], 'MAE Corrected': df['cor_dif']})
        stats=stats.append(normalized_df)
    
    
stats = stats.groupby('PFOV (degrees)').mean()
mean_uncorrected = stats['Mean Absolute Error'].mean()

pallete = sns.color_palette('colorblind', 8)
pallete_hex = pallete.as_hex()
#from matplotlib.font_manager import findfont

#fn = findfont("Helvetica", fontext="afm")
sns.set(rc={'figure.figsize':(3.35,2.8)}) #fig size in inches
sns.set(font="Arial")
sns.set_theme(style="ticks")
scatterplot = sns.lineplot(x = stats.index, y=stats['MAE Corrected'], color = pallete_hex[0])
#scatterplot = sns.lineplot(x = stats.index, y=stats['MAE Corrected'], color = pallete_hex[0])
#scatterplot.axhline(mean_uncorrected, ls='--', color = pallete_hex[7])
#scatterplot.text(62,.046, "Mean absolute error uncorrected albedo",fontsize = 10)
scatterplot.set_xlabel('PFOV (' + degree_sign + ')', fontsize = 12)
scatterplot.set_ylabel('Absolute Error', fontsize = 12)
scatterplot.set(ylim=(0.019, 0.023))
scatterplot.set(xlim=(60, 178))



plt.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/FOV_sensitivity_restricted.png', bbox_inches="tight",dpi=300)

#sns.scatterplot(x = stats['FOV'], y=stats['normalized_dif'])
    