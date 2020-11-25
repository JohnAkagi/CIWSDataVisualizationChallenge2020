# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 22:20:26 2020

@author: johna
"""

import pandas as pd
import matplotlib.pyplot as plt

class data_classified:
    def __init__(self, file):
        self.df = self.import_classified(file)
        self.indoor_df = self.get_indoor()
        self.outdoor_df = self.get_outdoor()
        
        self.data_start = self.df['DateTimeStart'].min()
        self.data_end = self.df['DateTimeStart'].max()
        self.data_duration = self.data_end - self.data_start
    
    def import_classified(self, file):
        ''' Imports the data classified by events '''
        class_data = pd.read_csv(file)
        
        class_data['DateTimeStart'] = pd.to_datetime(class_data['StartTime'])
        class_data['DateTimeEnd'] = pd.to_datetime(class_data['EndTime'])
        class_data['Day'] = class_data['DateTimeStart'].dt.day_name()
        
        minutes = class_data['DateTimeStart'].dt.minute/60.0
        seconds = class_data['DateTimeStart'].dt.second/3600.0
        class_data['Hour_Start'] = class_data['DateTimeStart'].dt.hour + minutes + seconds
        
        minutes = class_data['DateTimeEnd'].dt.minute/60.0
        seconds = class_data['DateTimeEnd'].dt.second/3600.0
        class_data['Hour_End'] = class_data['DateTimeEnd'].dt.hour + minutes + seconds
        

        
        values = class_data.columns
        
        
        
        # Format the measurements with a space between the description and unit
        for val in values:
            split_val = val.split('(')
            if len(split_val) > 1:
                split_val[1] = '(' + split_val[1]
                combined_val = " ".join(split_val)
                class_data = class_data.rename(columns={val:combined_val})
        
        # Change "closhwasher spelling
        class_data = class_data.replace({"clothwasher":"clothes washer"})
        # Capitalize the labesl
        labels = class_data.Label.unique()
        for lab in labels:
            class_data = class_data.replace({lab:lab.title()})
        
        return(class_data)
        
    def get_indoor(self):
        ''' Gets all the events that deal with indoor usage '''
        df = self.df;
        indoor_labels = ['Faucet','Toilet','Clothes Washer','Shower']
        indoor_df = df.loc[df.Label.isin(indoor_labels)]
        return(indoor_df)
        
    def get_outdoor(self):
        ''' Gets all the events that deal with outdoor usage'''
        
        df = self.df
        outdoor_labels = ['Hose','Irrigation']
        outdoor_labels = df.loc[df.Label.isin(outdoor_labels)]
        return(outdoor_labels)
        
    def total_cost(self, cost_gal):
        cost_dict = {}
        for name, group in self.df.groupby('Label'):
            total_vol = group.sum()['Volume (gal)']
            
            days = (group.DateTimeStart.max() - group.DateTimeStart.min()).days
            seconds = (group.DateTimeStart.max() - group.DateTimeStart.min()).seconds
            days = days + seconds/(24*3600.0)
            
            vol_day = total_vol/days
            vol_month = vol_day*30
            
            cost_dict[name] = vol_month*cost_gal
            
            
        return cost_dict
        
        
    def irrigation_events(self):
        
        irr_df = self.outdoor_df.groupby('Label').get_group('Irrigation')
        high_df = irr_df[irr_df['Volume (gal)'] > 100]
        num_high = high_df.shape[0]
        n_weeks = self.data_duration.days/7.0
        events_week = num_high/n_weeks
        print(high_df.groupby('Day').count())
        print(events_week)
        
    def irrigation_times(self):
        irr_df = self.outdoor_df.groupby('Label').get_group('Irrigation').copy()
        irr_df['Day'] = irr_df['DateTimeStart'].apply(lambda x: x.timetuple().tm_yday)
        
        start_times = irr_df['Hour_Start']
        end_times = irr_df['Hour_End']
        
        B = plt.boxplot(start_times)
        min_start = B['whiskers'][0].get_ydata()[1]
        B = plt.boxplot(end_times)
        max_end = B['whiskers'][1].get_ydata()[1]
        
        results = {}
        results['StartTime'] = min_start
        results['EndTime'] = max_end
        results['IdealStart'] = 4 # Per lawnDoctor, earliest water time is 4 AM
        results['IdealEnd'] = 9 # Per LawnDoctor, latest water time is 9 AM
        
        return(results)
        
        
    def equivalent_lawn(self, actual_acre):
        ''' Calculate what area of grass could be irrigated assuming .623 gal/week/sqft '''
        sqft2acre = 1/43560.0
        acre2sqft = 1/sqft2acre
        
        irr_df = self.outdoor_df.groupby('Label').get_group('Irrigation')
        total_gal = total_gal = irr_df.sum()['Volume (gal)']
        
        n_days = (irr_df.DateTimeStart.max() - irr_df.DateTimeStart.min()).days
        n_seconds = (irr_df.DateTimeStart.max() - irr_df.DateTimeStart.min()).seconds
        n_time = n_days + n_seconds/(24*3600)
        
        equiv_sqft = total_gal*7.0/(.623*n_time) # (gal/days)*(7 days/1 week)*(sqft * week/ .623 gal)
        equiv_acre = equiv_sqft*sqft2acre
        
        # Calculate the ideal amount of irrigation water
        actual_sqft = actual_acre * acre2sqft
        ideal_usage = actual_sqft * .623 * n_time / 7.0 # sqft * (.623 gal/ week*sqft)*days*(1 week/7 days)
        
        results = {}
        results['Actual Usage (gal)'] = total_gal
        results['Ideal Usage (gal)'] = ideal_usage
        results['Actual Area (acre)'] = actual_acre
        results['Equivalent Area (acre)'] = equiv_acre

        return results
    
    def get_shower_gpm(self):
        
        ideal_gpm = 2.0
        
        shower_df = self.df.groupby('Label').get_group('Shower')
        mean_gpm = shower_df['Flowrate (gpm)']
        
        results = {}
        results['Actual Flowrate (gpm)'] = mean_gpm
        results['Ideal Flowrate (gpm)'] = ideal_gpm
        
        return(results)
        
        
        
        