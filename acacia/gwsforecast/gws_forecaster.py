'''
Created on Nov 10, 2016

@author: stephane
'''
# -*- coding: utf-8 -*-
from __future__ import print_function
from django.shortcuts import get_object_or_404
from acacia.data.models import Series
"""
Created on Tue Aug 30 12:02:08 2016

@author: miriam
"""


import os
import numpy as np
import lmfit
import datetime
import pandas as pd
import pylab 
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)
# os.chdir('/home/stephane/eclipse_workspace/ModelMiriam/hornhuizen')
# def gws_forecast(histor_gws,histor_ev,histor_pt,forecast_et,forecast_pt,forecast_tmp):
def gws_forecast(df_gws_hist, df_et_hist, df_pt_hist, df_et_mean_fc, df_pt_mean_fc, df_tmp_mean_fc, df_et_std_fc, df_pt_std_fc, df_tmp_std_fc):
    
    #hist gw
    df_h_day = df_gws_hist.resample('d', how = 'mean')
    #hist evaporation 
    df_et_day = df_et_hist.resample('d', how = 'mean')
    df_et_day.fillna(value=None, method = 'ffill', inplace = True) #will continue filling nan with previous value, no restriction yet
    #hist precipitation
    df_pt_day = df_pt_hist.resample('d', how = 'sum') #
    df_pt_day.fillna(value=None, method = 'ffill', inplace = True) #will continue filling nan with previous value, no restriction yet
    
    
    df = df_h_day.join(df_pt_day)
    df_day = df.join(df_et_day)
    #creating arrays for lmfit 
    # Mean daily values for gw, pt and et using dataframes from spaarwater website
    data_day = np.zeros([len(df_h_day), 5])
    index = df_h_day.index.tolist()
    datetime_day = []
    for i in range (len(index)):
        a = index[i]
        datetime_day.append(a.to_datetime())
    
    for i in range (len(index)):
        x = datetime_day[i]
        data_day[i,0] = datetime.datetime.toordinal(x)
    
    data_day[:,1:4] = np.array(df_day)
    data_h = data_day[len(data_day)-300:-1,1]*100.0 
    Pt = data_day[len(data_day)-300:-1,2]/10.0    
    for i in range (len(Pt)):           #sets the nan values to the preceding value, does not have a limit pf nans in here yet.
        if np.isnan(Pt[i]) == True: 
            print (i, 'True')
            Pt[i] = Pt[i-1]         
    
    Et_nan = data_day[len(data_day)-300:-1,3]/100.0        
    Et = np.nan_to_num(Et_nan)  #sets all nan values to zero
    Pt_Et = Pt - Et
    hmin1 = data_h    
    
    #evaporation calculated with Makking, unit [W/m2]--> radiation, so the mean values need to be used
    #forecast data    
    #mean values    
    df_et_day_voorsp = df_et_mean_fc.resample('d', how = 'mean') #et
    df_pt_day_voorsp = df_pt_mean_fc.resample('d', how = 'sum') #pt
    df_tmp_day_voorsp = df_tmp_mean_fc.resample('d', how = 'mean') #tmp
    #standard deiviation
    df_et_day_voorsp_std = df_et_std_fc.resample('d', how = 'mean')
    df_pt_day_voorsp_std = df_pt_std_fc.resample('d', how = 'sum') 
    df_tmp_day_voorsp_std = df_tmp_std_fc.resample('d', how = 'mean')


###############################################################################
#functions for lmfit, calculation of forecasted groundwater level
############################################################################### 

#parameters for main equation
    def delta(bergingscoefficient, drainageweerstand) :
        delta = np.exp(-1/(bergingscoefficient * drainageweerstand)) #ATTENTION its e(-1/(b*d))
        return(delta)
    
    
    def omega(drainageweerstand, bergingscoefficient): 
        omega = drainageweerstand * (1.0 - delta(bergingscoefficient, drainageweerstand))    
        return(omega)
    
    
    def cw(drainageweerstand, qbot, hgem):
        cw = ((drainageweerstand * (qbot/10.0))*1) + hgem    #qbot is calculated from mm to cm
        return(cw)
            
    #function to fit the parameters
    def gws_op_t(params, data = None, weights = None) :  
        '''
        Function, which calculates the groundwater level depending on the parameters 
        drainageweerstand, bergingscoefficient, qbot (kwel), hgem (Average groundwater 
        level, hmin1 (groundwater level from the time step before and the precipitation)) 
        '''       
        vals = params.valuesdict()
        drainageweerstand = vals['drainweerstand']
        qbot = vals['qbot']
        hgem = vals['hgem']
        bergingscoefficient = vals['bergingscoefficient']
       
        model_h = np.zeros(len(Pt_Et))
        
        for i in range(1,len(Pt_Et)):
            model_h[i-1] = cw(drainageweerstand, qbot, hgem) + delta(bergingscoefficient, drainageweerstand) \
            * (hmin1[i-1] - cw(drainageweerstand, qbot, hgem)) + omega(drainageweerstand, bergingscoefficient) \
            * ((Pt_Et[i])/(1.0))
        model_h[model_h > 0.0] = 0.0
            
        if data_h is None: # if there is a gap in the measured data set this loop will fill in the calculated values from ht
            return model_h        
        else:
            h_res = model_h - data_h       
            print ('mean of residual: ', np.mean(model_h - data_h))        
            #print ('hmin1',hmin1)        
            return h_res
    
    ###############################################################################
    #create a set of parameters 
    ###############################################################################
    def optimize():
        
        params = lmfit.Parameters()
        params.add('bergingscoefficient', value=0.11, vary = True, min = 0.001, max = 0.3) #0.11
        params.add('drainweerstand', value=150.0, vary = True, min = 0.01, max = 1000.0) #165.0 units = days
        params.add('qbot', value=0.1, vary = True, min = -1.0, max = 1.0) #kwel #-1.0-1 [mm]
        params.add('hgem', value=-70.0, vary = True, min = -150.0, max = 0.0) #ontwateringsbasis   
   
        # do fit, here with leastsq model
        x = np.linspace(0, len(data_h)-1, len(data_h))
        args= x,  data_h
        kws  = {'options': {'maxiter':10}}
        minner = lmfit.Minimizer(gws_op_t, params, fcn_args=(args), fcn_kws = None) #{'nan_policy' = 'omit'}
    
        result = minner.minimize(method='leastsq')
        
        fitparamvals = result.params.valuesdict()
        
        bergingscoefficient = fitparamvals['bergingscoefficient']
        drainageweerstand = fitparamvals['drainweerstand']
        qbot = fitparamvals['qbot']
        hgem = fitparamvals['hgem']
        print('\n Best fitted parameters are: bergingscoefficient = ', bergingscoefficient, \
        'drainageweerstand = ', drainageweerstand, 'qbot = ',qbot, 'hgem = ', hgem)
     
        # calculate final result
        result_res = result.residual    
        
        h_calc = (data_h + result.residual)
        
        #try to plot calculated results vs the measured head values
        
        #plt.plot(data_h/100.0, 'ko')
        #plt.plot(Pt_Et, 'b')
        plt.plot(h_calc[:-1], 'k', label = 'model') 
        
        '''   
        try:
            pylab.plot(x, data_h, 'k')
            pylab.plot(x, h_calc, 'k--')
            pylab.show()
        except:
            pass
        '''
        return bergingscoefficient, drainageweerstand, qbot, hgem, data_h
    
        ###############################################################################
        #forecast values of pt and et
        ###############################################################################
        #getting data from the KNMI website (precipitation, temperature and evaporation)
        
    def data_voorsp():
        
        #getting mean voorspelling data
        data_day_voorsp = np.zeros([len(df_pt_day_voorsp), 4])
    
        ID = df_pt_day_voorsp.index.tolist()
        datetime_day = []
        for i in range (len(ID)):
            a = ID[i]
            datetime_day.append(a.to_datetime())
        
        for i in range (len(ID)):
            k = datetime_day[i]
            data_day_voorsp[i,0] = datetime.datetime.toordinal(k) #inserting date number
    
        df_pt_et_voorsp = df_pt_day_voorsp.join(df_et_day_voorsp)
        data_day_voorsp[:,1] = (np.array(df_pt_et_voorsp['apcpsfc_mean']))/10.0#inserting rainfall prediction, devide by 10 to get cm
    
        df_pt_et_tmp_voorsp = df_pt_et_voorsp.join(df_tmp_day_voorsp)
    
        ev_voorsp_w_m2 = np.array(df_pt_et_voorsp['pevprsfc_mean']) #unit = w/m2, needs to be changed to mm
        tmp_voorsp = np.array(df_pt_et_tmp_voorsp['tmp2m_mean'])
        pt_voorsp_mean = (np.array(df_pt_et_voorsp['apcpsfc_mean']))/10.0
    
        def et_cm():
            
            et_voorsp_cm = np.zeros([len(tmp_voorsp)])
        
            for i in range (len(tmp_voorsp)):
                L = 4185.5 * (751.78 - 0.5655 * tmp_voorsp[i])     
                et_voorsp_cm[i] = (ev_voorsp_w_m2[i]/L * 60 * 60 * 24)/10.0 # (kg * d-1 * m-2)/10 to get cm
            return et_voorsp_cm
        
        etcm = et_cm()
        meteo_voorsp = pt_voorsp_mean[-17:] - etcm[-17:]
                
        #getting standard deviation (MINIMUM/MAXIMUM) voorspelling data
        tmp_voorsp_std = np.array(df_tmp_day_voorsp_std)
        tmp_voorsp_min = np.zeros([len(tmp_voorsp_std)])
        tmp_voorsp_max = np.zeros([len(tmp_voorsp_std)])
        
        for i in range (len(tmp_voorsp_std)):
            tmp_voorsp_min[i] = tmp_voorsp[i] - tmp_voorsp_std[i]
            tmp_voorsp_max[i] = tmp_voorsp[i] + tmp_voorsp_std[i]
            
        et_voorsp_w_m2_std = np.array(df_et_day_voorsp_std)
        ev_voorsp_w_m2_min = np.zeros([len(ev_voorsp_w_m2)])
        ev_voorsp_w_m2_max = np.zeros([len(ev_voorsp_w_m2)])
        
        for i in range (len(ev_voorsp_w_m2)):
            ev_voorsp_w_m2_min[i] = ev_voorsp_w_m2[i] - et_voorsp_w_m2_std[i]
            ev_voorsp_w_m2_max[i] = ev_voorsp_w_m2[i] + et_voorsp_w_m2_std[i]

        
        pt_voorsp_std = (np.array(df_pt_day_voorsp_std))/10.0
        pt_voorsp_min = np.zeros([len(pt_voorsp_std)])
        pt_voorsp_max = np.zeros([len(pt_voorsp_std)])
        
        for i in range (len(pt_voorsp_std)):        
            pt_voorsp_min[i] = pt_voorsp_mean[i] - pt_voorsp_std[i]
            pt_voorsp_max[i] = pt_voorsp_mean[i] + pt_voorsp_std[i]
                
        for i in range (len(pt_voorsp_min)):
            if pt_voorsp_min[i] < 0:
                pt_voorsp_min[i]  = 0            
        for i in range (len(pt_voorsp_min)):
            if pt_voorsp_max[i] < 0:
                pt_voorsp_max[i]  = 0    
        
        data_day_voorsp_min = np.zeros([len(pt_voorsp_min), 4])
        data_day_voorsp_max = np.zeros([len(pt_voorsp_max), 4])
        
        ID = df_pt_day_voorsp.index.tolist()
        datetime_day = []
        for i in range (len(ID)):
            a = ID[i]
            datetime_day.append(a.to_datetime())
        
        for i in range (len(ID)):
            k = datetime_day[i]
            data_day_voorsp_min[i,0] = datetime.datetime.toordinal(k) #inserting date number
            data_day_voorsp_max[i,0] = datetime.datetime.toordinal(k)            
            
        data_day_voorsp_min[:,1] = pt_voorsp_min[:]#inserting rainfall prediction
        data_day_voorsp_max[:,1] = pt_voorsp_max[:]
        
    
        def et_cm_min():
            
            ev_voorsp_cm_min = np.zeros([len(pt_voorsp_min)])
        
            for i in range (len(ev_voorsp_cm_min)):
                L = 4185.5 * (751.78 - 0.5655 * tmp_voorsp_min[i])     
                ev_voorsp_cm_min[i] = (ev_voorsp_w_m2_min[i]/L * 60 * 60 * 24)/10.0 #kg * d-1 * m-2    
            return ev_voorsp_cm_min

        def et_cm_max():
            
            ev_voorsp_cm_max = np.zeros([len(pt_voorsp_max)])
        
            for i in range (len(pt_voorsp_max)):
                L = 4185.5 * (751.78 - 0.5655 * tmp_voorsp_max[i])     
                ev_voorsp_cm_max[i] = (ev_voorsp_w_m2_max[i]/L * 60 * 60 * 24)/10.0 #kg * d-1 * m-2    
            return ev_voorsp_cm_max
        
        etcm_min = et_cm_min()
        meteo_voorsp_min = pt_voorsp_mean[-17:] - etcm_min[-17:]

        etcm_max = et_cm_max()
        meteo_voorsp_max = pt_voorsp_mean[-17:] - etcm_max[-17:]
        
        return meteo_voorsp, meteo_voorsp_min, meteo_voorsp_max
            
    ###############################################################################
    #forecast caclulation
    ###############################################################################
    def voorsp_gw():
        
        meteo, meteo_min, meteo_max = data_voorsp()
        bergingscoefficient, drainageweerstand, qbot, hgem, data_h = optimize()
    
        voorspelling_h = np.zeros([17])
        voorspelling_h_min = np.zeros([17])        
        voorspelling_h_max = np.zeros([17])

        index = range(len(data_h)-2,len(data_h)+15) #creates a forecast for 10 days including an overlap of 2 days
        
        voorspelling_h[0:2] = data_h[index[0:2]] # fix this, here is something going wrong
        voorspelling_h_min[0:2] = data_h[index[0:2]]
        voorspelling_h_max[0:2] = data_h[index[0:2]]        
        
        
        for i in range(2,17): #insert parameter_new in here 
            voorspelling_h[i] = cw(drainageweerstand, qbot, hgem) + delta(bergingscoefficient, drainageweerstand) \
            * (voorspelling_h[i-1] - cw(drainageweerstand, qbot, hgem)) + omega(drainageweerstand, bergingscoefficient) \
            * ((meteo[i])/(1.0)) #ATTENTION: here it was orinally devided by 10 not -1         
            
            voorspelling_h_min[i] = cw(drainageweerstand, qbot, hgem) + delta(bergingscoefficient, drainageweerstand) \
            * (voorspelling_h_min[i-1] - cw(drainageweerstand, qbot, hgem)) + omega(drainageweerstand, bergingscoefficient) \
            * ((meteo_min[i])/(1.0))
            
            voorspelling_h_max[i] = cw(drainageweerstand, qbot, hgem) + delta(bergingscoefficient, drainageweerstand) \
            * (voorspelling_h_max[i-1] - cw(drainageweerstand, qbot, hgem)) + omega(drainageweerstand, bergingscoefficient) \
            * ((meteo_max[i])/(1.0))
        
        return voorspelling_h, voorspelling_h_min, voorspelling_h_max, data_h

    voorspelling_h, voorspelling_h_min, voorspelling_h_max, data_h = voorsp_gw()
    index = range(len(data_h)-2,len(data_h)+15)

    first_date_forecast = df_h_day.index[-3]
    forecast_indices = []
    for i in range (len(voorspelling_h)):
        forecast_indices.append(first_date_forecast + i)
    df_voorspelling_h = pd.DataFrame(data=voorspelling_h, index = forecast_indices, columns = ['fc_gws_mean'])
    df_voorspelling_h_min = pd.DataFrame(data=voorspelling_h_min, index = forecast_indices, columns = ['fc_gws_min'])
    df_voorspelling_h_max = pd.DataFrame(data=voorspelling_h_max, index = forecast_indices, columns = ['fc_gws_max'])
    
    df_h_day_cm = df_h_day[-300:] * 10.0
    join_1 = df_h_day_cm.join(df_voorspelling_h, how = 'outer')
    join_2 = join_1.join(df_voorspelling_h_min, how = 'outer')
    joined_together = join_2.join(df_voorspelling_h_max, how = 'outer')    
    
    
# 
#     pylab.plot(data_h, 'ko', label = 'gemeten data')
#     pylab.plot(index, voorspelling_h, 'b', label = 'gemiddelde grondwaterstand')
#     pylab.plot(index, voorspelling_h_min, 'g', label = 'minimale grondwaterstand' )
#     pylab.plot(index, voorspelling_h_max, 'r', label = 'maximale grondwaterstand')       
#     plt.legend(loc = 4)
#     plt.title('Grondwaterstand voorspelling in Hornhuizen [cm]')    
#     plt.ylabel('Diepte onder maaiveld')
#     plt.xlabel('Aantal dagen')    
#     pylab.show()
#     
    return joined_together

'''
test run
'''
# hist_gws = get_object_or_404(Series,pk=495) #grondwaterstand
# hist_ev = get_object_or_404(Series,pk=208) #EV24 lauwersoog
# hist_pt = get_object_or_404(Series,pk=722) #neerslag hornhuizen RP2
# forec_et = get_object_or_404(Series,pk=1085) #pevprsfc-mean
# forec_pt = get_object_or_404(Series,pk=1083) #apcpsfc_mean
# forec_tmp = get_object_or_404(Series,pk=1087) #tmp2m_mean
# gws_forecast(hist_gws,hist_ev,hist_pt,forec_et,forec_pt,forec_tmp)
# localhost:8000/gwsvoorspelling?hist_gws=495&hist_ev=208&hist_pt=772&forec_et=1085&forec_pt=1083&forec_tmp=1087
# get_object_or_404(Series,pk=).to_pandas().resample('d', how='mean')

# dataf = get_object_or_404(Series,pk=495).to_pandas()
# en dan dataf zo aanpassen dat het in het model werkt 



