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
        days = (self.data_end - self.data_start).days
        seconds = (self.data_end - self.data_start).seconds
        self.data_duration = days + seconds/(24*3600)
        
        # Ideal values
        self.ideal_toilet_gpf = 1.28
        self.moderate_toilet_gpf = 1.6
        self.ideal_faucet_gpm = 1.5
        self.ideal_shower_gpm = 2.0
        self.ideal_shower_duration = 5.0
        
        # Water cost (Logan)
        cost_kgal = 1.42
        self.cost_gal = cost_kgal/1000.0
    
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
        
        
    def get_irrigation_gpm(self, actual_acre):
        ''' Calculate water used as irrigation per month and compares that to an ideal value based on acrage
            Also calculates how much land you could water with current consumption but not currently used 
            Assumes .623 gal/sqft '''        
            
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
        
        # Calculate monthly usage
        month_usage = total_gal*30/n_time # Gallons/month
        ideal_month_usage = ideal_usage*30/n_time # Gallons/month
        
        # Calculate potential savings
        gal_saved_month = month_usage - ideal_month_usage
        dollar_saved = gal_saved_month*self.cost_gal
        
        results = {}
        results['Name'] = 'Irrigation Usage'
        results['Units'] = 'Gallons per Month'
        results['Actual Usage (gal)'] = month_usage
        results['Ideal Usage (gal)'] = ideal_month_usage
        results['Potential Savings ($)'] = dollar_saved
        results['Potential Savings (gal)'] = gal_saved_month
        #results['Actual Area (acre)'] = actual_acre
        #results['Equivalent Area (acre)'] = equiv_acre

        return results
    
    def get_shower_gpm(self):
        
        
        shower_df = self.df.groupby('Label').get_group('Shower').copy()
        mean_gpm = shower_df['Flowrate (gpm)'].mean()
        
        (dollar_saved_month, gal_saved_month) = self.calc_flow_savings(shower_df, self.ideal_shower_gpm)
        
        results = {}
        results['Name'] = 'Shower Flowrate'
        results['Units'] = 'Gallons per Minute'
        results['Actual Flowrate (gpm)'] = mean_gpm
        results['Ideal Flowrate (gpm)'] = self.ideal_shower_gpm
        results['Potential Savings ($)'] = dollar_saved_month
        results['Potential Savings (gal)'] = gal_saved_month
        
        return(results)
        
    def get_shower_time(self):
        shower_df = self.df.groupby('Label').get_group('Shower').copy()
        mean_gpm = shower_df['Duration (min)'].mean()
        
        (dollar_saved_month, gal_saved_month) = self.calc_time_savings(shower_df, self.ideal_shower_duration)
        
        results = {}
        results['Name'] = 'Shower Duration'
        results['Units'] = 'Minutes'
        results['Actual Duration (min)'] = mean_gpm
        results['Ideal Duration (min)'] = self.ideal_shower_duration
        results['Potential Savings ($)'] = dollar_saved_month
        results['Potential Savings (gal)'] = gal_saved_month
        
        return(results)
        
    def get_faucet_gpm(self):
        
        
        faucet_df = self.df.groupby('Label').get_group('Faucet').copy()
        mean_gpm = faucet_df['Flowrate (gpm)'].mean()
        
        (dollar_saved_month, gal_saved_month) = self.calc_flow_savings(faucet_df, self.ideal_faucet_gpm )
        
        
        results = {}
        results['Name'] = 'Faucet Flowrate'
        results['Units'] = 'Gallons per Minute'
        results['Actual Flowrate (gpm)'] = mean_gpm
        results['Ideal Flowrate (gpm)'] = self.ideal_faucet_gpm 
        results['Potential Savings ($)'] = dollar_saved_month
        results['Potential Savings (gal)'] = gal_saved_month
        
        return(results)
        
    def get_toilet_gpf(self):
        
        toilet_df = self.df.groupby('Label').get_group('Toilet').copy()
        mean_gal = toilet_df['Volume (gal)'].mean()
        
        (dollar_saved_month, gal_saved_month) = self.calc_vol_savings(toilet_df, self.ideal_toilet_gpf)
        
        results = {}
        results['Name'] = 'Toilet'
        results['Units'] = 'Gallons per Flush'
        results['Actual Usage (gal/flush)'] = mean_gal
        results['Ideal Usage (gal/flush)'] = self.ideal_toilet_gpf
        results['Typical Usage (gal/flush)'] = self.moderate_toilet_gpf
        results['Potential Savings ($)'] = dollar_saved_month
        results['Potential Savings (gal)'] = gal_saved_month
        
        return(results)
        
    def calc_vol_savings(self, df, ideal_vol):
        ''' Calculates the savings over month if volume for each event is capped'''
        
        df['IdealVolume'] = df['Volume (gal)']
        df.loc[df['IdealVolume'] > ideal_vol, 'IdealVolume'] = ideal_vol
        ideal_gal = df['IdealVolume'].sum()
        actual_gal = df['Volume (gal)'].sum()
        diff_gal = actual_gal - ideal_gal
        dollar_saved = diff_gal*self.cost_gal
        dollar_saved_month = dollar_saved*30/self.data_duration
        diff_gal_month = diff_gal*30/self.data_duration
        
        return(dollar_saved_month, diff_gal_month)
        
    def calc_flow_savings(self, df, ideal_flow):
        ''' Calculates the savings over a month if flow for each event is capped '''
        
        df['IdealFlow'] = df['Flowrate (gpm)']
        df.loc[df['IdealFlow'] > ideal_flow, 'IdealFlow'] = ideal_flow
        df['IdealVol'] = df['IdealFlow']*df['Duration (min)']
        ideal_gal = df['IdealVol'].sum()
        actual_gal = df['Volume (gal)'].sum()
        diff_gal = actual_gal - ideal_gal
        dollar_saved = diff_gal*self.cost_gal
        dollar_saved_month = dollar_saved*30/self.data_duration
        diff_gal_month = diff_gal*30/self.data_duration
        
        return(dollar_saved_month, diff_gal_month)
        
    def calc_time_savings(self, df, max_time):
        ''' Calculates the savings over a month if duration for each event is capped '''
        
        df['IdealDuration'] = df['Duration (min)']
        df.loc[df['IdealDuration'] > max_time, 'IdealDuration'] = max_time
        df['IdealVol'] = df['Flowrate (gpm)']*df['IdealDuration']
        ideal_gal = df['IdealVol'].sum()
        actual_gal = df['Volume (gal)'].sum()
        diff_gal = actual_gal - ideal_gal
        dollar_saved = diff_gal*self.cost_gal
        dollar_saved_month = dollar_saved*30/self.data_duration
        diff_gal_month = diff_gal*30/self.data_duration
        
        return(dollar_saved_month, diff_gal_month)
        
        
    def calc_dt_savings(self, df, dt):
        ''' Calculates the savings if duration is cut down by dt (min) '''
        
        df['IdealDuration'] = df['Duration (min)'] - dt
        df.loc[df['IdealDuration'] < 0, 'IdealDuration'] = 0
        df['IdealVol'] = df['Flowrate (gpm)']*df['IdealDuration']
        ideal_gal = df['IdealVol'].sum()
        actual_gal = df['Volume (gal)'].sum()
        diff_gal = actual_gal - ideal_gal
        dollar_saved = diff_gal*self.cost_gal
        dollar_saved_month = dollar_saved*30/self.data_duration
        diff_gal_month = diff_gal*30/self.data_duration
        
        return(dollar_saved_month, diff_gal_month)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        