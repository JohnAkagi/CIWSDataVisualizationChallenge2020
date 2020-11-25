# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 19:58:03 2020

@author: johna
"""
import matplotlib.pyplot as plt
import numpy as np


def icon_plot(amount):
    ''' Plots the amount in gallons using gallon icons. Rounds to nearest 1/4 '''
    
    # Read in the images used with the plots
    gal = plt.imread('../images/gallon.png')
    three_quart = plt.imread('../images/three_quart.png')
    half_gal = plt.imread('../images/half.png')
    quart = plt.imread('../images/quart.png')
    
    # Set the number of columns for the plots
    columns = 2
    
    # Determine the number of rows needed
    full_rows = int(np.ceil(np.floor(amount)/columns))
    remainder_rows = int(1 - np.ceil(full_rows*columns-amount))
    rows = full_rows + remainder_rows
    
    # Round the amount to quarter gallons
    remainder = np.round((amount - np.floor(amount))*4)/4
    gal_amount = np.floor(amount)
    rounded_amount = gal_amount + remainder
    
    # Due to how matplotlib handles subplots, there needs to be > 1 row
    if rows == 1:
        rows = 2
        empty_top = True
    else:
        empty_top = False
        
    
    fig, ax = plt.subplots(rows,columns,figsize=(columns,rows+1))
    
    # If an extra row was added to appease matplotlib, turn off all the axes
    if empty_top == True:
        for col_idx in np.arange(columns-1,-1,-1):
            ax[0,col_idx].axis('off')
        
    # Plot each whole number of gallons
    gal_count = 0;
    if rounded_amount >= 1:
        for row_idx in np.arange(rows-1,-1,-1):
            
            # Turn off axes for row
            for col_idx in np.arange(columns-1,-1,-1):
                ax[row_idx,col_idx].axis('off')
                
            # Plot whole gallons
            for col_idx in np.arange(columns-1,-1,-1):
                ax[row_idx,col_idx].imshow(gal)
                
                gal_count = gal_count + 1
                if gal_count >= gal_amount:
                    break
            if gal_count >= gal_amount:
                break   
            
    
    
    # Determine if the last row is supposed to be empty
    if empty_top:
        row_idx = 1
    else:
        row_idx = 0
    
    # Determine the column position for the remainder
    if gal_count%2 == 0:
        col_idx = 1
        # Turn off other axis on this row
        ax[row_idx,0].axis('off')
    else:
        col_idx = 0

    # Plot the remainder
    if remainder == 0.75:
        ax[row_idx,col_idx].imshow(three_quart)
        ax[row_idx,col_idx].axis('off')
        
    elif remainder == 0.5:
        ax[row_idx,col_idx].imshow(half_gal)
        ax[row_idx,col_idx].axis('off')
        
    elif remainder == 0.25:
        ax[row_idx,col_idx].imshow(quart)
        ax[row_idx,col_idx].axis('off')
        
    else:
        ax[row_idx,col_idx].axis('off')
        
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.subplots_adjust(wspace=0, hspace=0)
    return(fig, ax)
        
if __name__ == "__main__":
    fig, ax = icon_plot(1.3)
