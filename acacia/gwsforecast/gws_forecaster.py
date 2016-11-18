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

###############################################################################
#getting Pt, GW and Et time series in a pandas dataframe
###############################################################################
'''I'm using pandas, because there are lots of irregularities in the data set 
regarding the time and date of when the measurements were recorded. '''

os.chdir('/home/stephane/eclipse_workspace/ModelMiriam/hornhuizen')
def gws_forecast(histor_gws,histor_ev,histor_pt,forecast_et,forecast_pt,forecast_tmp):
    
    hist_gws = histor_gws.to_pandas().to_frame()
    hist_gws = hist_gws.resample('d', how='mean')
    hist_gws.fillna(inplace = True, method = 'bfill', limit = 7)
#     hist_gws.fillna(1.0, inplace = True, method = 'bfill', limit = 7))
    if hist_gws.isnull().any().any():
        logger.warning('Series %s replacement of nan values failed' % (histor_gws.name))
        return None
    
    hist_ev = histor_ev.to_pandas().to_frame()
    hist_ev = hist_ev.resample('d', how='mean')
    hist_ev.fillna(inplace = True, method = 'bfill', limit = 7)
    if hist_gws.isnull().any().any():
        logger.warning('Series %s replacement of nan values failed' % (histor_ev.name))
        return None

    hist_pt = histor_pt.to_pandas().to_frame()
#         hist_pt = hist_pt.resample('d', how='mean')
    hist_pt.fillna(0, inplace = True, limit = 7)
    if hist_gws.isnull().any().any():
        logger.warning('Series %s replacement of nan values failed' % (histor_pt.name))
        return None
    
    df = hist_gws.join(hist_pt)
    df_day = df.join(hist_ev)
      
    
    forec_et = forecast_et.to_pandas().to_frame()
    df_et_day_voorsp = forec_et.resample('d', how='mean')
    df_et_day_voorsp.fillna(1.0, inplace = True)
    if hist_gws.isnull().any().any():
        logger.warning('Series %s replacement of nan values failed' % (forecast_et.name))
        return None
    
    forec_pt = forecast_pt.to_pandas().to_frame()
    df_pt_day_voorsp = forec_pt.resample('d', how='sum')
    df_pt_day_voorsp.fillna(1.0, inplace = True)
    if hist_gws.isnull().any().any():
        logger.warning('Series %s replacement of nan values failed' % (forecast_pt.name))
        return None
    
    forec_tmp = forecast_tmp.to_pandas().to_frame()
    df_tmp_day_voorsp = forec_tmp.resample('d', how='mean')
    df_tmp_day_voorsp.fillna(1.0, inplace = True)
    if hist_gws.isnull().any().any():
        logger.warning('Series %s replacement of nan values failed' % (forecast_tmp.name))
        return None
    
    

    
    

  
#     
#     ''' voorspellingen  '''
#     df = pd.read_csv('downloaded16_11_11/pevprsfc_mean.csv', index_col=0, parse_dates=True, dayfirst=False)
#     df_et_day_voorsp = df.resample('d', how = 'mean')
#     df_et_day_voorsp.fillna(1.0, inplace = True)
#     df = pd.read_csv('downloaded16_11_11/apcpsfc_mean.csv', index_col=0, parse_dates=True, dayfirst=False)
#     df_pt_day_voorsp = df.resample('d', how = 'sum')
#     df_pt_day_voorsp.fillna(1.0, inplace = True)
#     df = pd.read_csv('downloaded16_11_11/tmp2m_mean.csv', index_col=0, parse_dates=True, dayfirst=False)
#     df_tmp_day_voorsp = df.resample('d', how = 'mean')
#     df_tmp_day_voorsp.fillna(1.0, inplace = True)

#     hist_gws = get_object_or_404(Series,pk=hist_gws).to_pandas().to_frame()
#     hist_gws = hist_gws.resample('d', how='mean')
#     hist_gws.fillna(1.0, inplace = True)
#     hist_ev = get_object_or_404(Series,pk=hist_ev).to_pandas().to_frame()
#     hist_ev = hist_ev.resample('d', how='mean')
#     hist_ev.fillna(1.0, inplace = True)
#     hist_pt = get_object_or_404(Series,pk=hist_pt).to_pandas().to_frame()
#     hist_pt = hist_pt.resample('d', how='mean')
#     hist_pt.fillna(1.0, inplace = True)
#     df = hist_gws.join(hist_pt)
#     df_day = df.join(hist_ev)
#       
    
    #using data from the spaarwater website
    # hist  gws
#     df = pd.read_csv('grondwaterstand.csv', index_col=0, parse_dates=True, dayfirst=False)
#     df_h_day = df.resample('d', how = 'mean')
#     # hist ev
#     df = pd.read_csv('ev24.csv', index_col=0, parse_dates=True, dayfirst=False)
#     df_et_day = df.resample('d', how = 'mean')
# #     hist precip.
#     df = pd.read_csv('neerslag_hornhuizen.csv', index_col=0, parse_dates=True, dayfirst=False)
#     df_pt_day = df.resample('d', how = 'mean')
#     df = df_h_day.join(df_pt_day)
#     df_day = df.join(df_et_day)


    
#     forec_et = get_object_or_404(Series,pk=forec_et)
#     forec_et = forec_et.resample('d', how='mean')
#     forec_pt = get_object_or_404(Series,pk=forec_pt)
#     forec_pt = forec_pt.resample('d', how='mean')
#     forec_tmp = get_object_or_404(Series,pk=forec_tmp)
#     forec_tmp = forec_tmp.resample('d', how='mean')

    data_day = np.zeros([len(hist_gws), 5])
    index = hist_gws.index.tolist()    


    #creating arrays for lmfit 
    # Mean daily values for gw, pt and et using dataframes from spaarwater website
    
    '''here she creates an combined historical data array called data_day'''
#     data_day = np.zeros([len(df_h_day), 5])
#     index = df_h_day.index.tolist()
   
    
    datetime_day = []
    for i in range (len(index)):
        a = index[i]
        datetime_day.append(a.to_datetime())
    
    for i in range (len(index)):
        x = datetime_day[i]
        data_day[i,0] = datetime.datetime.toordinal(x)
    
    data_day[:,1:4] = np.array(df_day)
    data_day[:,4] = data_day[:,2] - data_day[:,3]
    
       # last cell contains nan, thats why -2
    '''here she throws away the last value because Et has a NAN at [-1]'''
    data_h = data_day[len(data_day)-141:-1,1] 
#     Pt = data_day[len(data_day)-141:-1,2]
#     Et = data_day[len(data_day)-141:-1,3] # last two cells = nan, thats why -2
    Pt_Et = data_day[len(data_day)-141:-1,4]
    hmin1 = data_h
    

###############################################################################
#functions for lmfit, calculation of forecasted groundwater level
############################################################################### 

#parameters for main equation
    def delta(bergingscoefficient, drainageweerstand) :
        delta = np.exp((bergingscoefficient * drainageweerstand)) #ATTENTION its e(-1/(b*d))
        return(delta)
    
    
    def omega(drainageweerstand, bergingscoefficient): 
        omega = drainageweerstand * (1.0 - delta(bergingscoefficient, drainageweerstand))    
        return(omega)
    
    
    def cw(drainageweerstand, qbot, hgem):
        cw = ((drainageweerstand * (qbot/10))*1) + hgem    
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
            * ((Pt_Et[i])/(-1.0))
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
        params.add('bergingscoefficient', value=0.11, vary = True, min = 0.001, max = 0.99) #0.11
        params.add('drainweerstand', value=150.0, vary = True, min = 1.0, max = 165.0) #165.0
        params.add('qbot', value=0.1, vary = True, min = -1.0, max = 1.0) #kwel #-1.0-1
        params.add('hgem', value=-0.6, vary = True, min = -1.5, max = 0.0) #ontwateringsbasis   
   
        # do fit, here with leastsq model
        x = np.linspace(0, len(data_h)-1, len(data_h))
        args= x,  data_h
        kws  = {'options': {'maxiter':10}}
        minner = lmfit.Minimizer(gws_op_t, params, fcn_args=(args), fcn_kws = None)
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
        
        return bergingscoefficient, drainageweerstand, qbot, hgem, data_h
        ###############################################################################
        #forecast values of pt and et
        ###############################################################################
        #getting data from the KNMI website (precipitation, temperature and evaporation)
        
    def data_voorsp():
        
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
        data_day_voorsp[:,1] = np.array(df_pt_et_voorsp['apcpsfc_mean'])#inserting rainfall prediction
    
        df_pt_et_tmp_voorsp = df_pt_et_voorsp.join(df_tmp_day_voorsp)
    
        ev_voorsp_w_m2 = np.array(df_pt_et_voorsp['pevprsfc_mean']) #unit = w/m2, needs to be changed to mm
        tmp_voorsp = np.array(df_pt_et_tmp_voorsp['tmp2m_mean'])
    
        def et_mm():
            
            et_voorsp_mm = np.zeros([len(tmp_voorsp)])
        
            for i in range (len(tmp_voorsp)):
                L = 4185.5 * (751.78 - 0.5655 * tmp_voorsp[i])     
                et_voorsp_mm[i] = ev_voorsp_w_m2[i]/L * 60 * 60 * 24 #kg * d-1 * m-2    
            return et_voorsp_mm
        
        data_day_voorsp[:,2] = et_mm()
        data_day_voorsp[:,3] = data_day_voorsp[:,1] - data_day_voorsp[:,2]
        meteo_voorsp = data_day_voorsp[:,3]
        return meteo_voorsp
            
    ###############################################################################
    #forecast caclulation
    ###############################################################################
    def voorsp_gw():
        
        meteo = data_voorsp()
        bergingscoefficient, drainageweerstand, qbot, hgem, data_h = optimize()
    
        voorspelling_h = np.zeros([17])
        index = range(len(data_h)-2,len(data_h)+15) #creates a forecast for 10 days including an overlap of 2 days
       
        voorspelling_h[0:2] = data_h[index[0:2]] # fix this, here is something going wrong
        
        for i in range(2,17): #insert parameter_new in here 
            voorspelling_h[i] = cw(drainageweerstand, qbot, hgem) + delta(bergingscoefficient, drainageweerstand) \
            * (voorspelling_h[i-1] - cw(drainageweerstand, qbot, hgem)) + omega(drainageweerstand, bergingscoefficient) \
            * ((meteo[i])/(-1.0)) #ATTENTION: here it was orinally devided by 10 not -1   
        
        return voorspelling_h, data_h

    voorspelling_h, data_h = voorsp_gw()
    index = range(len(data_h)-2,len(data_h)+15)



#     pylab.plot(data_h, 'k')
#     pylab.plot(index, voorspelling_h, 'r')
#     pylab.show()
#     data_h = pd.DataFrame(data_h)
    
    historisch_gws = df_day.ix[:,0][:-1]
    first_date_forecast = historisch_gws.index[-2]
    historisch_gws = pd.DataFrame(historisch_gws)
    forecast_indices = []
    for i in range(len(voorspelling_h)):
        forecast_indices.append(first_date_forecast+i)
    
    voorspelling_h = pd.DataFrame(data=voorspelling_h, index = forecast_indices, columns = ['voorspelde_gws'])
#     voorspelling_h =  pd.DataFrame(voorspelling_h)

    joined_together = historisch_gws.join(voorspelling_h, how='outer')
    joined_together.columns = ['Grondwaterstand', 'voorspelde_gws']
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



