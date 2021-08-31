# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 15:38:50 2021

@author: x51b783
"""
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

path_to_tarp = 'D:/field_data/tarp/tarps_plot.csv'

df = pd.read_csv(path_to_tarp)

df['Surface'] = df['Surface'].map({'bare ground': 'bare asphalt', 
                                   'plain tarp': 'grey tarp', 
                                   'black center': 'grey tarp black center',
                                   'black side': 'grey tarp black side'})

pallete = sns.color_palette('colorblind', 4)
pallete_hex = pallete.as_hex()
sns.set(rc={'figure.figsize':(6,4)}) #fig size in inches
sns.set(font="Arial")
sns.set_theme(style="ticks")


scatterplot = sns.scatterplot(data = df, x = 'Height (m)', y = 'Albedo', hue = 'Surface', marker="$\circ$", ec="face", s=40, palette = pallete)
scatterplot.set_xlabel('Height (m)', fontsize = 12)
scatterplot.set_ylabel('Albedo', fontsize = 12)

#plt.savefig('C:/Users/x51b783/Documents/Mirror/Masters/writing/frontiers_figures/tarps_plot.png', bbox_inches="tight",dpi=300)