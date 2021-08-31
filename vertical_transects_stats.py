# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 15:05:41 2021

@author: x51b783
"""
import pandas as pd
import os
import seaborn as sns


path = 'D:/field_data/YC/YC20210428/merged/vertical_transects/'

stats = pd.DataFrame(columns = ['rmse', 'bias', 'method', 'agl_alt'])

df_weighted = pd.DataFrame(columns = ['corrected_albedo_ss', 'cos_avg_ls8_ss', 'albedo', 'agl_alt', 'agl_alt_binned'])
df_mean = pd.DataFrame(columns = ['corrected_albedo_ss', 'cos_avg_ls8_ss', 'albedo', 'agl_alt', 'agl_alt_binned'])

cut_labels = [30, 40, 50, 60, 70]
cut_bins = [20, 30, 40, 50, 60, 70]
cut_labels = [22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70]
cut_bins = [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70]

for file in os.listdir(path):
    
    df = pd.read_csv(path+file)
    
    
    
    df['agl_alt_binned'] = pd.cut(df['agl_alt'], bins=cut_bins, labels = cut_labels)
    
    #rmse = ((df['corrected_albedo_ss'] - df['cos_avg_ls8_ss']) ** 2).mean() ** .5
    #bias = (df['corrected_albedo_ss'] - df['cos_avg_ls8_ss']).mean()
    #method = df.iloc[0]['method']
    
    print(file)
    if file.endswith('mean.csv'):
        df_mean=df_mean.append(df[['corrected_albedo_ss', 
                          'cos_avg_ls8_ss', 
                          'albedo',
                          'agl_alt',
                          'agl_alt_binned']])
        
    else:
        df_weighted=df_weighted.append(df[['corrected_albedo_ss', 
                          'cos_avg_ls8_ss', 
                          'albedo',
                          'agl_alt',
                          'agl_alt_binned']])
    
    #stats=stats.append({'rmse': rmse, 'bias': bias, 'method': method}, ignore_index = True)

for alt in cut_labels:
    
    alt_mean = df_mean.loc[df_mean['agl_alt_binned']==alt]
    rmse_mean = ((alt_mean['corrected_albedo_ss'] - alt_mean['cos_avg_ls8_ss']) ** 2).mean() ** .5
    bias_mean = (alt_mean['corrected_albedo_ss'] - alt_mean['cos_avg_ls8_ss']).mean()
    
    alt_weighted = df_weighted.loc[df_weighted['agl_alt_binned']==alt]
    rmse_weighted = ((alt_weighted['corrected_albedo_ss'] - alt_weighted['cos_avg_ls8_ss']) ** 2).mean() ** .5
    bias_weighted = (alt_weighted['corrected_albedo_ss'] - alt_weighted['cos_avg_ls8_ss']).mean()
    
    stats=stats.append({'rmse': rmse_mean, 'bias': bias_mean, 'method': 'mean', 'agl_alt': alt}, ignore_index = True)
    stats=stats.append({'rmse': rmse_weighted, 'bias': bias_weighted, 'method': 'weighted', 'agl_alt': alt}, ignore_index = True)


 
   
pallete = sns.color_palette('colorblind', 8)
pallete_hex = pallete.as_hex()
sns.set(rc={'figure.figsize':(3.35,4)}) #fig size in inches
sns.set(font="Arial")
sns.set_theme(style="ticks")

#scatterplot = sns.scatterplot(data = stats, x = 'agl_alt', y = 'rmse', hue = 'method')
scatterplot = sns.scatterplot(data = stats, x = 'agl_alt', y = 'bias', hue = 'method')

#scatterplot.text(33,.046, "Mean ebsolute error uncorrected albedo",fontsize = 8)
scatterplot.set_xlabel('AGL altitude (m)', fontsize = 12)
scatterplot.set_ylabel('RMSE', fontsize = 12)
#scatterplot.set(ylim=(0.019, 0.022))
#scatterplot.set(xlim=(30, 75))



#plt.savefig('D:/field_data/YC/FOV_sensitivity_restricted.tiff', bbox_inches="tight",dpi=300)
