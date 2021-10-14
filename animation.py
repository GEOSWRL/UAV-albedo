# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 15:07:59 2021

@author: x51b783
"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import cv2
import os
import glob

degree_sign = u"\N{DEGREE SIGN}"

def build_timelapse(image_dir, output_file):
    #path to output video
    
    files = os.listdir(image_dir)
    
    img_array = []
    i=0
    size = []
    
    #loop through images in directory that end with .jpg
    for filename in files:
        
        #read in image
        img = cv2.imread(image_dir+filename)
        img_array.append(img)
    
        #on first pass through, get image properties
        if i==0:
            height, width, layers = img.shape
            size = (width,height)
    
        i=1
    
    
    #create output file
    out = cv2.VideoWriter(output_file,cv2.VideoWriter_fourcc(*'DIVX'), 10, size)
    
    #write images to frames
    for i in range(len(img_array)):
        out.write(img_array[i])
    
    out.release()

    
def create_plots(csv_in, path_out, filename_prefix):
    df=pd.read_csv(csv_in)

    PFOVs = np.arange(30, 180, 2.5)
    x=0
    sns.set(rc={'figure.figsize':(3.35,2.8)}) #fig size in inches
    sns.set(font="Arial")
    sns.set_theme(style="ticks")  
    plt.legend(bbox_to_anchor=(1.01, 1),
           borderaxespad=0)
    
    for PFOV in PFOVs:  
    
        df1=df.loc[df['PFOV']==PFOV]
    
        fig, ax = plt.subplots()
    
        ax.set_xlabel('AGL Altitude (m)', fontsize=12)
        ax.set_ylabel('Albedo', fontsize=12)
    
        ax.set_xlim(30,65)
        ax.set_ylim(.3,.78)
        
        sns.lineplot(x=df['alt_agl'], y=df1['uncorrected_albedo'], label = 'uncorrected UAV')
        sns.lineplot(x=df['alt_agl'], y=df1['corrected_albedo'], label = 'corrected UAV')
        sns.lineplot(x=df['alt_agl'], y=df1['ls8_albedo'], label = 'LS8')
        
        ax.text(22,0.18, '\nPFOV: ' + str(PFOV) + degree_sign,fontsize = 10)
        
        
        
        if x<=9:
            fig.savefig(path_out + filename_prefix + '0' + str(x) + '.jpg', bbox_inches="tight",dpi=300)
        
        else:
            fig.savefig(path_out + filename_prefix + str(x) + '.jpg', bbox_inches="tight",dpi=300)
        
        x+=1
        
        fig = None
        ax = None

csv_in = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/02_corrected_albedo/02_vertical_transects/02_FOV/20210428_YC_VT5_FOV.csv' 
path_out = 'C:/Users/x51b783/Documents/Mirror/Masters/writing/FIRS/frontiers_figures/animation/VT5/'
filename_prefix = 'VT5_FOV_'
#create_plots(csv_in, path_out, filename_prefix)

image_dir = 'C:/Users/x51b783/Documents/Mirror/Masters/writing/FIRS/frontiers_figures/animation/VT5/'
output_file = 'C:/Users/x51b783/Documents/Mirror/Masters/writing/FIRS/frontiers_figures/animation/VT5.avi'

build_timelapse(image_dir, output_file)