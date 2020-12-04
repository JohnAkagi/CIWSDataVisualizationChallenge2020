# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 22:13:05 2020

@author: johna
"""
import data_processing as dat

from data_classified import data_classified





if __name__ == "__main__":
    
    filepath = '../mailer'
    plot_acre = .28
    
    # Get data from file
    file = "../data/Classified_Events.csv"
    classified_data = data_classified(file)
    
    # Plot means using icons and save
    dat.generate_icon_plots(classified_data.indoor_df, filepath)
    
    # Plot irrigation times
    irr_times = classified_data.irrigation_times()
    dat.plot_water_times(irr_times, filepath)
    
    # Plot average faucet gpm and ideal
    faucet_gpm = classified_data.get_faucet_gpm()
    dat.plot_ideals(faucet_gpm, filepath)

    # Plot average shower gpm and ideal
    shower_gpm = classified_data.get_shower_gpm()
    dat.plot_ideals(shower_gpm, filepath)
    
    # Plot average shower time and ideal
    shower_time = classified_data.get_shower_time()
    dat.plot_ideals(shower_time, filepath)
    
    # Plot average toilet gallons per flush
    toilet_gpf = classified_data.get_toilet_gpf()
    dat.plot_ideals(toilet_gpf, filepath)
    
    # Plot irrigation usage
    irr_gpm = classified_data.get_irrigation_gpm(plot_acre)
    dat.plot_ideals(irr_gpm, filepath)