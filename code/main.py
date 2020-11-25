# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 22:13:05 2020

@author: johna
"""
import data_processing as dat

from data_classified import data_classified





if __name__ == "__main__":
    cost_kgal = 1.42
    cost_gal = cost_kgal/1000.0
    
    # Get data from file
    file = "../data/Classified_Events.csv"
    classified_data = data_classified(file)
    
    # Plot means using icons and save
    dat.generate_icon_plots(classified_data.indoor_df, '../mailer')