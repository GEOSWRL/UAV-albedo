# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 14:35:19 2021

@author: x51b783
"""
import pandas as pd
import os
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

path = 'D:/UAV-albedo/data_test_dir/03_UAV_snow_data/02_processed_data/03_topo_correction/02_corrected_albedo/02_vertical_transects/02_FOV/'

degree_sign = u"\N{DEGREE SIGN}"

df_all = pd.DataFrame()

for file in os.listdir(path):
    
    df = pd.read_csv(path+file)

    df_all = df_all.append(df)


stats = pd.DataFrame(columns = ['PFOV', 'rmse', 'r2'])

alt_dependence = pd.DataFrame(columns = ['PFOV', 'slope', 'y_intercept', 'r2'])

#FOVs = np.multiply([30,35,40,45,50,55,60,65,70,75,80,85,89],2)
#PFOVs = np.multiply([30,50,70,80, 87.5],2)
PFOVs = np.arange(30, 180, 2.5)
for PFOV in PFOVs:
    
    data_chunk = df_all.loc[df_all['PFOV'] == PFOV]
    
    rmse = ((data_chunk['ls8_albedo'] - data_chunk['corrected_albedo']) ** 2).mean() ** .5
    
    stats = stats.append({'PFOV': PFOV, 'rmse': rmse}, ignore_index = True)
    
    x = np.vstack(data_chunk['alt_agl'])
    y=data_chunk['corrected_raw_error']
    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    alt_dependence = alt_dependence.append({'PFOV': PFOV, 'slope': regr.coef_, 'y_intercept': regr.intercept_, 'r2': regr.score(x,y)}, ignore_index=True)

##############################################################################################

'''

#sns.set(rc={'figure.figsize':(3.35,2.8)}) #fig size in inches
sns.set(font="Arial")
sns.set_theme(style="ticks")  
sns.set_palette(sns.color_palette("viridis", n_colors = 13)) 

def abline(slope, intercept, a):
    """Plot a line from slope and intercept"""
    
     
    #axes[a].set_xlabel('AGL Altitude (m)', fontsize=12)
    #axes[a].set_ylabel('Error', fontsize=12)


fig, axes = plt.subplots(5, 1, sharex=True,sharey=True, figsize=(3.35,5))


a=0
for index, row in alt_dependence.iterrows():
    
    x_vals = np.linspace(20, 70, num=2)
    y_vals = row['y_intercept'] + row['slope'] * x_vals
    ax = sns.lineplot(ax = axes[a], x=x_vals, y=y_vals, color='black')
    ax = sns.scatterplot(ax = axes[a],x=df.loc[df['PFOV']==row['PFOV']]['alt_agl'], y=df.loc[df['PFOV']==row['PFOV']]['corrected_raw_error'], alpha=0.5, color='grey')
    ax.set_ylabel('')
    
    if a<2:
        ax.text(56,-.01, '\nPFOV: ' + str(row['PFOV']) + degree_sign,fontsize = 10)
        ax.text(56,-.09, "$r^2$: " + str(round(row['r2'],2)),fontsize = 10)
    if a==2:
        ax.set_ylabel('Error\n(Landsat albedo - Corrected albedo)', fontsize=12)
        ax.text(56,0.02, '\nPFOV: ' + str(row['PFOV']) + degree_sign,fontsize = 10)
        ax.text(56,-.08, "$r^2$: " + str(round(row['r2'],2)),fontsize = 10)
    
    if a>2:
        ax.text(56,0.018, '\nPFOV: ' + str(row['PFOV']) + degree_sign,fontsize = 10)
        ax.text(56,-.048, "$r^2$: " + str(round(row['r2'],2)),fontsize = 10)
        
    a+=1

ax.set_xlabel('Altitude AGL (m)', fontsize=12)

#sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=60, vmax=180))
# fake up the array of the scalar mappable. Urgh...
#sm._A = []
#plt.colorbar(sm, label='PFOV (' + degree_sign + ')')
#plt.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/VT_FOV_alt2.png', bbox_inches="tight",dpi=300)
'''




##############################################################################################

stats['PFOV'] = (stats['PFOV']).astype(str).str[:-2]

pallete = sns.color_palette('colorblind', 10)
pallete_hex = pallete.as_hex()

#Create combo chart
sns.set(rc={'figure.figsize':(7,4)}) #fig size in inches
sns.set(font="Arial")
sns.set_style("whitegrid")
sns.set_style('ticks')
fig, ax1 = plt.subplots()

#bar plot creation
#ax1.set_title('Average Percipitation Percentage by Month', fontsize=16)

ax1 = sns.violinplot(data=df_all, x='PFOV', y='corrected_raw_error', color=pallete[8])



#specify we want to share the same x-axis
ax2 = ax1.twinx()

#line plot creation
#ax2.set_ylabel('Avg Percipitation %', fontsize=16)


ax2 = sns.lineplot(data=stats, x='PFOV', y='rmse', linestyle = '--', color=pallete[7], label = 'RMSE')

ax1.set_xlabel('PFOV (' + degree_sign + ')', fontsize=12)
ax1.set_ylabel('Error\n(Landsat albedo - Corrected albedo)', fontsize=12)
ax2.set_ylabel('RMSE', fontsize=12)
plt.legend(loc='lower left')
plt.xticks(ha='center')
ax1.grid(False)
ax2.grid(False)

#show plot
plt.show()

#fig.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/VT_FOV.tiff', bbox_inches="tight",dpi=300)

