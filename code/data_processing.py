# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 23:04:31 2020

@author: John Akagi

This file contains functions for basic data proceesing and visualization
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from icon_plot import icon_plot
import plotting_params as param 


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
        fig.text(.75, .06,name.replace(" ","\n"),fontsize=param.title_fontsize, transform=fig.dpi_scale_trans)
        amnt_str = "{:.2f} Gal".format(mean)
        fig.suptitle(amnt_str,fontsize=param.title_fontsize,x=.55)
        
        filename = "{}/{}_icon.png".format(save_path,name).replace(" ","")
        fig.savefig(filename,format='png')
        
def plot_water_times(results_dict, save_path):
    ''' Plots the actual and ideal times to water the lawn
        The results_dict should have the fields 'StartTime','EndTime','IdealStart', and 'IdealEnd' 
        with the times as hours and parts of hours '''
    
    
    # Have to finagle the xaxis a little so it looks ok with dates
    # The date in here is just a dummy date and doesn't matter
    times = pd.date_range('2020-10-06', periods=1, freq='H')
    
    # Xaxis is in days since epoch so convert everything to that scale
    start_time = mdates.date2num(times[0]) + results_dict['StartTime']/24.0
    duration = (results_dict['EndTime'] - results_dict['StartTime'])/24.0
    start_time_ideal = mdates.date2num(times[0]) + results_dict['IdealStart'] /24.0
    duration_ideal = (results_dict['IdealEnd'] - results_dict['IdealStart'])/24.0
    
    if start_time + duration <= start_time_ideal + duration_ideal:
        text_msg = 'Usage is\nExcellent'
        actual_color = param.sucsess_color
    else:
        text_msg = 'Water Earlier\nTo Save Water' 
        actual_color = param.fail_color
    
    #Location where the bars will be
    bar_height = .1
    actual_y = .66 - bar_height/2.0
    ideal_y = .33 - bar_height/2.0
    plot_height = 1.0
    
    fig, ax = plt.subplots(figsize=(8,3))

    ax.broken_barh([(start_time, duration)],(actual_y, bar_height), facecolors=actual_color)
    ax.broken_barh([(start_time_ideal, duration_ideal)],(ideal_y,bar_height), facecolors=param.ideal_color)
    ax.plot(( start_time_ideal, start_time_ideal), (0,plot_height), color=param.ideal_color, alpha=.4)
    ax.plot(( start_time_ideal+duration_ideal, start_time_ideal+duration_ideal), (0,plot_height), color=param.ideal_color, alpha=.4)
    
    # Set Y axis labels and ticks
    ax.set_yticks([ideal_y+bar_height/2.0, actual_y+bar_height/2.0])
    ax.set_yticklabels(['Ideal Times to Water', 'When You Water'])
    ax.set_ylim((0,plot_height))
    
    # Set X axis with the hour of the day
    ax.set_xlim(mdates.date2num(times[0]),mdates.date2num(times[0]) + 1)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0,25,2) ))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%I %p') )
    ax.tick_params(axis='x', rotation=70)
    ax.tick_params(axis='x', labelsize=param.text_fontsize )
    ax.tick_params(axis='y', labelsize=param.text_fontsize )
    
    
    ax.text( start_time_ideal + duration_ideal + .3 , plot_height/4, text_msg,fontsize=param.text_fontsize,color=actual_color)
    
    fig.suptitle('Irrigation Times',fontsize=param.title_fontsize)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    filename = "{}/water_times.png".format(save_path).replace(" ","")
    fig.savefig(filename,format='png')
    
def plot_ideals(results, save_path):
    
    #values = np.empty(len(results.keys() - 1))
    values = np.empty(2)
    label = ['Actual','Ideal']
    
    for key in results.keys():
        if key == 'Name':
            continue
        if 'Ideal' in key:
            values[1] = results[key]
            label[1] = 'Ideal'
        if 'Actual' in key:
            values[0] = results[key]
            label[0] = 'Actual'
        if 'Savings' in key and '$' in key:
            savings_dollar = results[key]
            savings_unit = 'Dollars'
        if 'Savings' in key and 'gal' in key:
            savings_gallon = results[key]
            savings_unit = 'gal'
        if 'Units' in key:
            units = results[key]
            
    if values[1] >= values[0]:
        actual_color = param.sucsess_color
        text_msg = 'Usage is\nExcellent'
        x_pos = .75
    else:
        actual_color = param.fail_color
        #text_msg = 'Potential Savings:\n ${:.2f} per Month'.format(savings)
        text_msg = '{:.2f} gallons\nWasted per Month'.format(savings_gallon)
        x_pos = .52
        

    fig, ax = plt.subplots(figsize=(3.5,4))
    idx = [1]
    width = .5
    ax.bar(idx[0] - width/2, values[0], width, color=actual_color)
    ax.bar(idx[0] + width/2, values[1], width, color=param.ideal_color)
    
    max_val = max(values)
    ax.set_ylabel(units, fontsize=param.text_fontsize)
    ax.set_ylim(0, max_val*1.5)
    
    ax.set_xticks([idx[0] - width/2, idx[0] + width/2])
    ax.set_xticklabels(label, fontsize=param.text_fontsize)
    ax.tick_params(axis='x', rotation=70)
    
    ax.tick_params(axis='x', labelsize=param.text_fontsize )
    ax.tick_params(axis='y', labelsize=param.text_fontsize )
    
    ax.text(x_pos, max_val*1.2,text_msg,fontsize=param.text_fontsize,color=actual_color)
    
    fig.suptitle(results['Name'],fontsize=param.title_fontsize)
    
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    filename = "{}/{}.png".format(save_path,results['Name']).replace(" ","")
    fig.savefig(filename,format='png')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
