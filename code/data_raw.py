# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 23:04:38 2020

@author: johna
"""


import pandas as pd

class data_raw:
    def __init__(self, file):
        self.df = self.import_raw(file)
        
    def import_raw():
        ''' Imports and prepares the raw data '''
        
        raw_data = pd.read_csv('../data/Raw_Data.csv',header=3)
        
        # Get the pulse to gallon conversion
        with open('../data/Raw_Data.csv','r') as f:
            f.readline()
            f.readline()
            data = f.readline()
            
        split_data = data.split()
        conversion = float(split_data[2])
        
        raw_data['Vol (gal)'] = raw_data.Pulses*conversion
        
        return raw_data