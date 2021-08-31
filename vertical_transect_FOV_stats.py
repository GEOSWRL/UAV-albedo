# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 19:51:02 2021

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


degree_sign = u"\N{DEGREE SIGN}"

path = 'D:/field_data/YC/YC20210428/merged/vertical_transects/FOV/'

df_all = pd.DataFrame(columns = ['FOV', 'albedo', 'corrected_albedo', 'ls8_albedo', 'agl_alt'])

for file in os.listdir(path):
    
    df = pd.read_csv(path+file)
    df['FOV'] = df['FOV'].astype(int)*2
    df['absolute_error'] = df['ls8_albedo'] - df['corrected_albedo']
    df_all = df_all.append(df)

df_all['FOV'].loc[df_all['FOV'] == 118] = 120
stats = pd.DataFrame(columns = ['FOV', 'rmse', 'r2'])

alt_dependence = pd.DataFrame(columns = ['FOV', 'slope', 'y_intercept', 'r2'])

#FOVs = np.multiply([30,35,40,45,50,55,60,65,70,75,80,85,89],2)
FOVs = np.multiply([30,50,70,80, 89],2)

for FOV in FOVs:
    
    data_chunk = df_all.loc[df_all['FOV'] == FOV]
    
    rmse = ((data_chunk['ls8_albedo'] - data_chunk['corrected_albedo']) ** 2).mean() ** .5
    
    stats = stats.append({'FOV': FOV, 'rmse': rmse}, ignore_index = True)
    
    x = np.vstack(data_chunk['agl_alt'])
    y=data_chunk['absolute_error']
    regr = linear_model.LinearRegression()
    regr.fit(x, y)
    alt_dependence = alt_dependence.append({'FOV': FOV, 'slope': regr.coef_, 'y_intercept': regr.intercept_, 'r2': regr.score(x,y)}, ignore_index=True)

##############################################################################################



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
    ax = sns.scatterplot(ax = axes[a],x=df.loc[df['FOV']==row['FOV']]['agl_alt'], y=df.loc[df['FOV']==row['FOV']]['absolute_error'], alpha=0.5, color='grey')
    ax.set_ylabel('')
    
    if a<2:
        ax.text(56,-.01, '\nPFOV: ' + str(row['FOV']) + degree_sign,fontsize = 10)
        ax.text(56,-.09, "$r^2$: " + str(round(row['r2'],2)),fontsize = 10)
    if a==2:
        ax.set_ylabel('Error\n(Landsat albedo - Corrected albedo)', fontsize=12)
        ax.text(56,0.02, '\nPFOV: ' + str(row['FOV']) + degree_sign,fontsize = 10)
        ax.text(56,-.08, "$r^2$: " + str(round(row['r2'],2)),fontsize = 10)
    
    if a>2:
        ax.text(56,0.018, '\nPFOV: ' + str(row['FOV']) + degree_sign,fontsize = 10)
        ax.text(56,-.048, "$r^2$: " + str(round(row['r2'],2)),fontsize = 10)
        
    a+=1

ax.set_xlabel('Altitude AGL (m)', fontsize=12)

#sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=60, vmax=180))
# fake up the array of the scalar mappable. Urgh...
#sm._A = []
#plt.colorbar(sm, label='PFOV (' + degree_sign + ')')
plt.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/VT_FOV_alt2.png', bbox_inches="tight",dpi=300)





##############################################################################################
'''
stats['FOV'] = (stats['FOV']).astype(str).str[:-2]

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

ax1 = sns.violinplot(data=df_all, x='FOV', y='absolute_error', color=pallete[8])



#specify we want to share the same x-axis
ax2 = ax1.twinx()

#line plot creation
#ax2.set_ylabel('Avg Percipitation %', fontsize=16)


ax2 = sns.lineplot(data=stats, x='FOV', y='rmse', linestyle = '--', color=pallete[7], label = 'RMSE')

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
'''
