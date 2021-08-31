# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 23:12:10 2021

@author: x51b783
"""

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

data_dirs=['D:/field_data/YC/YC20210311/merged/', 
          'D:/field_data/YC/YC20210318/merged/', 
          'D:/field_data/YC/YC20210428/merged/',
          ]

######################################### scatter/lineplot #################################################

df_summary=pd.DataFrame(columns = ['Uncorrected RMSE', 'RMSE Corrected Albedo', 'AGL Altitude (m)', 'Topography Source', 'Date'])

for data_dir in data_dirs: 
    for filename in os.listdir(data_dir):
        
        
        
        topo_source = ''
        rmse_uncorrected=0
        rmse_corrected=0
        
        if filename.endswith('.csv'):
            d=data_dir[19:27]
            d_str=''
            if d == '20210311':
                d_str = 'Mar. 11, 2021'
            if d == '20210318':
                d_str = 'Mar. 18, 2021'
            if d == '20210428':
                d_str = 'Apr. 28, 2021'
            
            df = pd.read_csv(data_dir+filename)
            rmse_uncorrected = ((df['albedo'] - df['cos_avg_ls8_ss']) ** 2).mean() ** .5
            rmse_corrected = ((df['corrected_albedo_ss'] - df['cos_avg_ls8_ss']) ** 2).mean() ** .5
            
            if filename.endswith('m.csv'):
                topo_source = 'Snow Surface SfM'
            
            if filename.endswith('bg.csv'):
                topo_source = 'Bare-ground SfM'
            
            if filename.endswith('USGS.csv'):
                topo_source = '3DEP 1/3 Arc Second'
                
            df_summary = df_summary.append({'Uncorrected': rmse_uncorrected,
                                            'Corrected': rmse_corrected,
                                            'AGL Altitude (m)':int(filename[7:9]),
                                            'Topography Source':topo_source, 
                                            'Date': d_str}, ignore_index = True)

df_melted = pd.melt(df_summary, id_vars=['Date', 'AGL Altitude (m)', 'Topography Source'], 
                    value_vars=['Uncorrected','Corrected'])
df_melted.rename(columns = {'value':'UAV Albedo RMSE', 'variable': 'RMSE'}, inplace = True)

sns.set(font="Arial")
sns.set_theme(style="ticks")  
sns.set_palette(sns.color_palette('colorblind', 10)) 
            
dates = ['Mar. 11, 2021', 'Mar. 18, 2021', 'Apr. 28, 2021']

fig, axes = plt.subplots(1, 3, sharex=False,sharey=True, figsize=(7,2.5))
        
sns.stripplot(ax = axes[0], data = df_melted.loc[(df_melted['Date'] == 'Mar. 11, 2021') & (df_melted['RMSE']=='Corrected')], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source',s=5, alpha=0.7, jitter=0.15)
sns.stripplot(ax = axes[1], data = df_melted.loc[(df_melted['Date'] == 'Mar. 18, 2021') & (df_melted['RMSE']=='Corrected')], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source',s=5, alpha=0.7, jitter=0.15)
sns.stripplot(ax = axes[2], data = df_melted.loc[(df_melted['Date'] == 'Apr. 28, 2021') & (df_melted['RMSE']=='Corrected')], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source',s=5, alpha=0.7, jitter=0.15)

sns.stripplot(ax = axes[0], data = df_melted.loc[(df_melted['Date'] == 'Mar. 11, 2021') & (df_melted['RMSE']=='Uncorrected')], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source',s=5, alpha=0.7, jitter=0.15, marker = 's')
sns.stripplot(ax = axes[1], data = df_melted.loc[(df_melted['Date'] == 'Mar. 18, 2021') & (df_melted['RMSE']=='Uncorrected')], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source',s=5, alpha=0.7, jitter=0.15, marker = 's')
sns.stripplot(ax = axes[2], data = df_melted.loc[(df_melted['Date'] == 'Apr. 28, 2021') & (df_melted['RMSE']=='Uncorrected')], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source',s=5, alpha=0.7, jitter=0.15, marker = 's')

axes[1].set(ylabel = '')
axes[2].set(ylabel = '')
#sns.scatterplot(ax = axes[1], data = df_melted.loc[df_melted['Date'] == 'Mar. 18, 2021'], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source', style= 'RMSE',s=80, alpha=0.65)
#sns.scatterplot(ax = axes[2], data = df_melted.loc[df_melted['Date'] == 'Apr. 28, 2021'], x = 'AGL Altitude (m)', y = 'UAV Albedo RMSE', hue = 'Topography Source', style= 'RMSE',s=80, alpha=0.65)

axes[0].text(.8,.24, 'Mar. 11, 2021',fontsize = 10)
axes[1].text(.8,.24, 'Mar. 18, 2021',fontsize = 10)
axes[2].text(.8,.24, 'Apr. 28, 2021',fontsize = 10)


plt.ylabel('RMSE', fontsize=12)
axes[0].legend([],[], frameon=False)
axes[1].legend([],[], frameon=False)
plt.legend(bbox_to_anchor=(1.01, 1),
           borderaxespad=0)
axes[2].set(ylabel = '')

plt.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/topo_source_altitude3.tiff', bbox_inches="tight",dpi=300)
plt.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/topo_source_altitude3.png', bbox_inches="tight",dpi=300)
###############################################################################################################

###################################################### topography source comparison #######################################
'''
data_dirs = ['D:/field_data/YC/YC20210311/merged/', 
             'D:/field_data/YC/YC20210318/merged/', 
             'D:/field_data/YC/YC20210428/merged/']

df_summary=pd.DataFrame(columns = ['Uncorrected Albedo', 'Corrected Albedo', 
                                   'LS8 Albedo', 'AGL Altitude', 'Topography Source', 'Date'])
sns.set(rc={'figure.figsize':(7,4)})
sns.set(font="Arial")
sns.set_theme(style="ticks")  
sns.set_palette(sns.color_palette('colorblind', 10)) 
for data_dir in data_dirs:
    for filename in os.listdir(data_dir):
        d=data_dir[19:27]
        d_str=''
        if d == '20210311':
            d_str = 'Mar. 11, 2021'
        if d == '20210318':
            d_str = 'Mar. 18, 2021'
        if d == '20210428':
            d_str = 'Apr. 28, 2021'
            
        topo_source = ''
        rmse_uncorrected=0
        rmse_corrected=0
            
        if filename.endswith('.csv'):
                
            df = pd.read_csv(data_dir+filename)
                
            if filename.endswith('m.csv'):
                topo_source = 'Snow Surface SfM'
                
            if filename.endswith('bg.csv'):
                topo_source = 'Bare-ground SfM'
                
            if filename.endswith('USGS.csv'):
                topo_source = '3DEP 1/3 Arc Second'
                    
            df_summary = df_summary.append(pd.DataFrame({'Uncorrected Albedo': df['albedo'],
                                                'Corrected Albedo': df['corrected_albedo_ss'],
                                                'LS8 Albedo': df['cos_avg_ls8_ss'],
                                                'AGL Altitude':[int(filename[7:9])]* len(df),
                                                'Topography Source':[topo_source] * len(df), 
                                                'Date': [d_str]*len(df)}), ignore_index = True)



df_filtered = df_summary.loc[df_summary['AGL Altitude'] == 20]

df_ss = df_filtered.loc[df_filtered['Topography Source'] == 'Snow Surface SfM']['Corrected Albedo']
df_bg = df_filtered.loc[df_filtered['Topography Source'] == 'Bare-ground SfM']['Corrected Albedo'].to_numpy()
df_usgs = df_filtered.loc[df_filtered['Topography Source'] == '3DEP 1/3 Arc Second']['Corrected Albedo'].to_numpy()

df_ls8 = df_filtered.loc[df_summary['Topography Source'] == 'Snow Surface SfM']['LS8 Albedo']
df_uncorr = df_filtered.loc[df_summary['Topography Source'] == 'Snow Surface SfM']['Uncorrected Albedo']

df_plot = pd.DataFrame(columns = ['Date', 'Uncorrected Albedo', 'Snow Surface SfM', 'Bare-ground SfM', '3DEP 1/3 Arc Second', 'LS8 Albedo'])

df_plot['Date'] = df_filtered.loc[df_filtered['Topography Source'] == 'Snow Surface SfM']['Date']


df_plot['Uncorrected Albedo'] = df_uncorr
df_plot['Snow Surface SfM'] = df_ss
df_plot['Bare-ground SfM'] = df_bg
df_plot['3DEP 1/3 Arc Second'] = df_usgs
df_plot['LS8 Albedo'] = df_ls8
            
df_melted = pd.melt(df_plot, id_vars=['Date'], value_vars=['Uncorrected Albedo','Snow Surface SfM','Bare-ground SfM','3DEP 1/3 Arc Second','LS8 Albedo'])

fig, ax = plt.subplots(figsize=(7,3))
ax = sns.boxplot(data = df_melted, x="Date", y='value', hue='variable')
ax.set_title('20 m AGL', fontsize=12)
ax.set_ylabel('Albedo')
plt.setp(ax.get_xticklabels(), rotation=0)
plt.legend(bbox_to_anchor=(1.01, 1),
           borderaxespad=0)
plt.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/topo_sourceC.png', bbox_inches="tight",dpi=300)

##########################################################Kruskall-Wallace##################################


# Perform Kruskal-Wallis Test 
df_kw = df_summary.loc[(df_summary['Date'] == 'Mar. 18, 2021') & (df_summary['AGL Altitude'] == 20)]
dates = ['Mar. 11, 2021', 'Mar. 18, 2021', 'Apr. 28, 2021']

altitudes = [10,15,20,30]
groups = ['Snow Surface SfM','Bare-ground SfM','3DEP 1/3 Arc Second']
df_kwresults = pd.DataFrame(columns = ['Date', 'Altitude', 'group1', 'group2', 'p-value'])
                            
for date in dates:
    df_date = df_summary.loc[df_summary['Date'] == date]
    
    for alt in altitudes:
        
        df_alt = df_date.loc[df_date['AGL Altitude'] == alt]
        
        for group1 in groups:
            
            df_group1 = df_alt.loc[df_alt['Topography Source'] == group1]['Corrected Albedo']
            
            for group2 in groups:
            
                df_group2 = df_alt.loc[df_alt['Topography Source'] == group2]['Corrected Albedo']
                kw = stats.kruskal(df_group1, df_group2)
                
                df_kwresults = df_kwresults.append({'Date': date, 
                                                    'Altitude': alt, 
                                                    'group1': group1, 
                                                    'group2': group2, 
                                                    'p-value': round(kw.pvalue,3)}, ignore_index=True)
                
kwresults_filtered = df_kwresults.loc[((df_kwresults['group1'] == 'Snow Surface SfM') & (df_kwresults['group2'] == 'Bare-ground SfM')
                                       | (df_kwresults['group1'] == 'Snow Surface SfM') & (df_kwresults['group2'] == '3DEP 1/3 Arc Second')
                                       | (df_kwresults['group1'] == '3DEP 1/3 Arc Second') & (df_kwresults['group2'] == 'Bare-ground SfM'))]
            
            
'''















