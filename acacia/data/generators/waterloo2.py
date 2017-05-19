# -*- coding: utf-8 -*-
from __future__ import print_function
'''
The program serves to calculate how much water should be added to a field
by drip irrigation in order for the soil moisture tension to remain within
the optimal water availability range for a certain crop. 

The prediction is based on the following:
    - Measurements of soil moisture tension Psi (daily average) at a critical
    depth in soil [kPa];
    - Reference evaporation data from the meteorological service [mm day-1]
    - Precipitation data from field measurements [mm day-1]
    - Predictions of precipitation for next period [mm day-1]
    
Created on Fri Mar  3 16:58:11 2017

@author: Maarten Waterloo
'''

__author__ = "Dr. Maarten J. Waterloo <maarten.waterloo@acaciawater.com>"
__version__ = "1.0"
__release__ = "1.0.1"
__date__ = "May 2017"

#import modules

import os
import numpy as np
#import lmfit
import datetime
import pandas as pd
#import pylab 
#import matplotlib.pyplot as plt

###############################################################################
# Functions
###############################################################################


def process_data(dtnow, psi_data, p_data, ev24_data, crop_factor, HindcastDays,
                 P_crit, dpF_ini,crop_type):
    '''
    Calculate median pF change and evaporation rates on dry and wet days based
    on measured pF data at critical depth and Makkink evaporation data.
    Data used are those from midnight to midnight. Insert daily data for 
    hindcast period in a dataframe  

    '''
 
    backperiod= datetime.timedelta(HindcastDays)
    #Define hindcast period
    HCPeriod= pd.date_range(dtnow-backperiod, dtnow)
     
    #Get daily means of pF for hindcast period
    df_psi = psi_data.resample('D').mean()
    df_psi = df_psi.reindex(HCPeriod)
#    df_psi = df_psi.loc[HCPeriod]
    
    #Calculate the difference between daily means
    df_psi['delta_pF']= df_psi['pF'].diff(1)
    
    #Calculate daily precipitation totals for hindcast period
    df_p = p_data.resample('D').sum()
    df_p = df_p.loc[HCPeriod]
    P_today = df_p.loc[dtnow,'P']
    
    #Calculate daily reference evaporation totals for hindcast period
    df_ev24 = ev24_data.loc[HCPeriod]
    
    #Get crop factor for today
    cf_today = crop_factor.loc[dtnow,crop_type]

    # Join data series
    df_mdata = df_psi.join(df_p.join(df_ev24))

    # Calculate pF change and ETm for dry days
    df_drydays= df_mdata.loc[df_mdata['P'] < P_crit]
    df_drydays= df_drydays.loc[df_drydays['delta_pF'] > 0.0]    
    if df_drydays['delta_pF'].count() < 2:
        pF_rise= dpF_ini
        mean_dryETm = df_mdata['ETm'].mean()
    else:
        pF_rise = df_drydays['delta_pF'].median()
        mean_dryETm = df_drydays['ETm'].mean()
        
    # Calculate changes for rainy days
    df_wetdays= df_mdata.loc[df_mdata['P'] > P_crit]
    df_wetdays= df_wetdays.loc[df_wetdays['delta_pF'] < 0.0]
    if df_wetdays['delta_pF'].count() < 2:
        pF_fall= -(dpF_ini)
        mean_wetETm = df_mdata['ETm'].mean()
    else:
        pF_fall = df_wetdays['delta_pF'].median()
        mean_wetETm = df_wetdays['ETm'].mean()
    
    return pF_rise, mean_dryETm, pF_fall, mean_wetETm, P_today, cf_today, df_mdata


def predict_irrigation(dtnow, psi_data, ev24_data, px_min, px_max, crop_factor,\
                       pF_rise, pF_fall, mean_dryETm, df_irrpred, pF_crit,\
                       ForecastDays, P_today, cf_today, irr_mult, irr_eff,crop_type):
    '''
    Function to calculate water needs for irrigation based on soil pF status,
    predicted precipitation en expected changes in pF values.
    
    '''

    # Get mean, min and max daily precipitation for the next 10-day period
    PrePeriod= datetime.timedelta(ForecastDays)
    
    # get recent midnight value of pF
    #pF_init= psi_data.loc[pd.Timestamp(dtnow),'pF']
    pF_init= psi_data.loc[dtnow,'pF']
    
    # Define ForeCast period
    FCPeriod= pd.date_range(dtnow, dtnow + PrePeriod)
        
    # Get min, mean and max daily precipitation forecasts for forecast period
    df_pred_minP = px_min.loc[FCPeriod,'p_min']
    df_pred_maxP = px_max.loc[FCPeriod,'p_max']
    
    #Get crop factors
    df_cf = crop_factor.loc[FCPeriod,crop_type]

    pF_ini= pF_init
    
    # If today's rainfall is higher than ETm, no need to irrigate next day
    j=0    
    if P_today > irr_mult * cf_today * mean_dryETm and pF_init < 3:
        df_irrpred.loc[dtnow + datetime.timedelta(1),'irr_min'] = 0.
        df_irrpred.loc[dtnow + datetime.timedelta(1),'irr_max'] = 0.
        pF_ini = pF_ini + pF_fall
        df_irrpred.loc[dtnow + datetime.timedelta(1),'pF_min'] = pF_ini
        df_irrpred.loc[dtnow + datetime.timedelta(1),'pF_min'] = pF_ini
        df_irrpred.loc[dtnow + datetime.timedelta(1),'p_min'] = \
        df_pred_minP.loc[dtnow + datetime.timedelta(1)]
        df_irrpred.loc[dtnow + datetime.timedelta(1),'p_max'] = \
        df_pred_maxP.loc[dtnow + datetime.timedelta(1)]
        j=1
    
    # Make P_min, pF and irrigation predictions 
    for i in range(1, ForecastDays+1-j):
        date = dtnow + datetime.timedelta(i) + datetime.timedelta(j)
        df_irrpred.loc[date,'p_min'] = df_pred_minP.loc[date]
        # Check if the current pF value plus expected rise are above critical
        # value and see if predicted minumum precipitation would be enough to
        # compensate for evapotranspiration, if not then irrigate    
        if pF_ini > pF_crit and df_pred_minP.loc[date] < \
        (df_cf.loc[date] * mean_dryETm): 
            df_irrpred.loc[date,'irr_min'] = irr_mult * (df_cf.loc[date] *\
            mean_dryETm) / irr_eff
            pF_ini = pF_ini + pF_fall
            df_irrpred.loc[date,'pF_min'] = pF_ini
        elif pF_ini + pF_rise > pF_crit and df_pred_minP.loc[date] < \
        (df_cf.loc[date] * mean_dryETm):
            df_irrpred.loc[date,'irr_min'] = (df_cf.loc[date] * mean_dryETm) / \
            irr_eff
            pF_ini = pF_ini
            df_irrpred.loc[date,'pF_min'] = pF_ini
        elif pF_ini + pF_rise > pF_crit and df_pred_minP.loc[date] > \
        (df_cf.loc[date] * mean_dryETm):
            df_irrpred.loc[date,'irr_min']  = 0.
            pF_ini = pF_ini + pF_fall
            df_irrpred.loc[date,'pF_min'] = pF_ini
        elif pF_init + pF_rise < pF_crit and df_pred_minP.loc[date] > \
        irr_mult * (df_cf.loc[date] * mean_dryETm):
            df_irrpred.loc[date,'irr_min']  = 0.
            pF_ini = pF_ini + pF_fall
            df_irrpred.loc[date,'pF_min'] = pF_ini
        else:
            df_irrpred.loc[date,'irr_min']  = 0.
            pF_ini = pF_ini + pF_rise
            df_irrpred.loc[date,'pF_min'] = pF_ini
            
    pF_ini= pF_init
            
    # Make P_max, pF and irrigation predictions 
    for i in range(1, ForecastDays+1-j):
        date = dtnow + datetime.timedelta(i) + datetime.timedelta(j)
        df_irrpred.loc[date,'p_max'] = df_pred_maxP.loc[date]
        # Check if the current pF value plus expected rise are above critical
        # value and see if predicted minumum precipitation would be enough to
        # compensate for evapotranspiration, if not then irrigate    
        if pF_ini > pF_crit and df_pred_maxP.loc[date] < \
        df_cf.loc[date] * mean_dryETm: 
            df_irrpred.loc[date,'irr_max'] = irr_mult * (df_cf.loc[date] *\
                          mean_dryETm) / irr_eff
            pF_ini = pF_ini + pF_fall
            df_irrpred.loc[date,'pF_max'] = pF_ini
        elif pF_ini + pF_rise > pF_crit and df_pred_maxP.loc[date] < \
        (df_cf.loc[date] * mean_dryETm):
            df_irrpred.loc[date,'irr_max'] = (df_cf.loc[date] * mean_dryETm) /\
            irr_eff
            pF_ini = pF_ini
            df_irrpred.loc[date,'pF_max'] = pF_ini
        elif pF_ini + pF_rise > pF_crit and df_pred_maxP.loc[date] > \
        (df_cf.loc[date] * mean_dryETm):
            df_irrpred.loc[date,'irr_max']  = 0.
            pF_ini = pF_ini + pF_fall
            df_irrpred.loc[date,'pF_max'] = pF_ini
        elif pF_ini + pF_rise < pF_crit and df_pred_maxP.loc[date] > \
        irr_mult * (df_cf.loc[date] * mean_dryETm):
            df_irrpred.loc[date,'irr_max']  = 0.
            pF_ini = pF_ini + pF_fall
            df_irrpred.loc[date,'pF_max'] = pF_ini
        else:
            df_irrpred.loc[date,'irr_max']  = 0.
            pF_ini = pF_ini + pF_rise
            df_irrpred.loc[date,'pF_max'] = pF_ini
            
    return df_irrpred
            
def run(psi_data, ev24_data, p_data, px_mean, px_max, px_min, crop_factor, dtnow = datetime.date.today()):
    # Change to data driectory    
#     os.chdir('../data')
    
    # Constants and start time
    crop_type='Potato' # Crop type for selecting crop factor to use in calculations
    irr_eff = 0.8 # irrigation efficiency factor
    irr_mult = 1.1 # Multiplier for additional irrigation needed to decrease soil pF
    ForecastDays = 5 # Forecast period
    HindcastDays = 10 # Period to go back for determining Delta pF
    dpF_ini = 0.1 # Default rise in pF
    P_crit = 1.5 # Minimum precipitation to define wet day
    pF_crit = 2.7 # Critical pF value above which irrigation needs to occur
#     dtnow = datetime.date.today() # Start date is today
#     dtnow = datetime.date(2016,6,10)

    # Read data, use date/time column as index
#     psi_data = pd.read_csv('psi_ref_20cm.csv',header=0, names=['Date','psi'], \
#                            index_col=0, parse_dates=True, dayfirst=False)
#     ev24_data= pd.read_csv('ev24_nw_beerta.csv',header=0, names=['Date','ETm'],\
#                             index_col=0, parse_dates=True, dayfirst=False)
#     p_data= pd.read_csv('533-neerslag.csv', header=0, names=['Date','P'], \
#                          index_col=0, parse_dates=True, dayfirst=False)
#     #px_mean= pd.read_csv('apcpsfc_mean.csv', header=0, names=['Date','Pmean'], \
#                           #index_col=0, parse_dates=True, dayfirst=False)
#     px_max= pd.read_csv('apcpsfc_max.csv', header=0, names=['Date','Pmax'], \
#                          index_col=0, parse_dates=True, dayfirst=False)
#     px_min= pd.read_csv('apcpsfc_min.csv', header=0, names=['Date','Pmin'], \
#                          index_col=0, parse_dates=True, dayfirst=False)
#     crop_factor= pd.read_csv('cropfactors.csv', header=0,\
#                              names=['Date','Potato','Onion','Cereals','Corn',\
#                                     'Sugarbeet','Bulbs'], index_col=0,\
#                                     parse_dates=True, dayfirst=False)
    
    #Convert EV24 data to mm
    ev24_data['ETm'] = ev24_data['ETm']/10.
    
    # Calculate pF value from psi
    psi_data['pF'] = np.log10(-10*psi_data['psi'])
    
    # Create dataframe for output
    index = pd.date_range(dtnow + datetime.timedelta(1), periods=ForecastDays,\
                          freq='D')
    columns = ['p_min','p_max','pF_min','pF_max','irr_min','irr_max']
    df_irrpred = pd.DataFrame(index=index, columns=columns)
    df_irrpred.index.name='date'
    
    # calculate statistics from hindcast period data
    pF_rise,mean_dryETm,pF_fall,mean_wetETm,P_today,cf_today,df_data = \
    process_data(dtnow, psi_data, p_data, ev24_data, crop_factor,HindcastDays, P_crit,\
                 dpF_ini,crop_type)
    
    df_irrigate = predict_irrigation(dtnow, psi_data, ev24_data, px_min, \
                                     px_max, crop_factor, pF_rise, pF_fall, mean_dryETm,\
                                     df_irrpred, pF_crit, ForecastDays, P_today, cf_today,\
                                     irr_mult, irr_eff,crop_type)

    df_alldata=pd.merge(df_data,df_irrigate,how='outer',left_index=True,\
                        right_index=True)
    return df_alldata

#    print(df_alldata)
#    
#     plt.figure()
#         #plt.xlabel('Datum')
#     ax = df_alldata.plot(secondary_y=['P','p_min','p_max','irr_min','irr_max','psi'])
#     ax.set_ylabel('pF', fontsize=14)
#     ax.right_ax.set_ylabel('P en Irrigation [mm]', fontsize=14)
#     ax.set_title('Irrigatie voorspelling')
#       
# if __name__ == "__main__":
#     main()
    