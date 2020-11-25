# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 23:04:31 2020

@author: John Akagi

This file contains functions for basic data proceesing and visualization
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from icon_plot import icon_plot


def plot_means(df):
    try:
        mean_values = df.groupby('Label').mean()
    except KeyError:
        print('Column \'Label\' does not exist.')
        print('Is this the classified data?')
        
    all_keys = mean_values.keys()
    
    for key in all_keys:
        fig, ax = plt.subplots()
        mean_values[key].plot.bar(ax=ax)
        ax.set_xlabel('Source')
        ax.set_ylabel(key)
        plt.tight_layout()
        
def generate_icon_plots(indoor_df, save_path):
    
    for name, group in indoor_df.groupby('Label'):
        mean = group.mean()['Volume (gal)']
        (fig, ax) = icon_plot(mean)
        fig.text(.01,.5,name,rotation=90,fontsize=16)
        amnt_str = "{:.2f} Gal".format(mean)
        fig.suptitle(amnt_str,fontsize=16,x=.55)
        
        filename = "{}/{}_icon.png".format(save_path,name).replace(" ","")
        fig.savefig(filename,format='png')
        
def plot_water_times(results_dict, save_path):
    
    
    # Have to finagle the xaxis a little so it looks ok with dates
    # The date in here is just a dummy date and doesn't matter
    times = pd.date_range('2020-10-06', periods=1, freq='H')
    
    # Xaxis is in days since epoch so convert everything to that scale
    start_time = mdates.date2num(times[0]) + results_dict['StartTime']/24.0
    duration = (results_dict['EndTime'] - results_dict['StartTime'])/24.0
    start_time_ideal = mdates.date2num(times[0]) + results_dict['IdealStart'] /24.0
    duration_ideal = (results_dict['IdealEnd'] - results_dict['IdealStart'])/24.0
    
    #Location where the bars will be
    actual_y = .3
    ideal_y = .1
    bar_height = .1
    
    fig, ax = plt.subplots()

    ax.broken_barh([(start_time, duration)],(actual_y, bar_height), facecolors='black')
    ax.broken_barh([(start_time_ideal, duration_ideal)],(ideal_y,bar_height), facecolors='black')
    
    ax.set_yticks([ideal_y+bar_height/2.0, actual_y+bar_height/2.0])
    ax.set_yticklabels(['Ideal Times', 'Actual Times'])
    
    ax.set_xlim(mdates.date2num(times[0]),mdates.date2num(times[0]) + 1)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0,25,1) ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I %p') )
    ax.tick_params(axis='x', rotation=70)
    fig.tight_layout()
        
    
    
