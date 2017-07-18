'''
Created on May 8, 2017

@author: theo
'''
from acacia.data.models import MeetLocatie
from acacia.data.generators.generic import GenericCSV
import datetime
from StringIO import StringIO
import waterloo3 as waterloo
import pandas as pd
import pytz

class Gift(GenericCSV):
    
    def download(self, **kwargs):

        mloc = MeetLocatie.objects.get(pk=1)                #Borgsweer Perceel 1
        psi_data = mloc.series_set.get(pk=kwargs.get('psi', 959)).to_pandas()  #Potential P1 (MPS-6)
        ev24_data = mloc.series_set.get(pk=kwargs.get('ev24', 36)).to_pandas()  #EV24
        p_data = mloc.series_set.get(pk=kwargs.get('p', 161)).to_pandas()    #Precipitation P1 (ECRN-100)
        px_mean = mloc.series_set.get(pk=kwargs.get('pmean', 816)).to_pandas()   #apcpsfc_mean
        px_std = mloc.series_set.get(pk=kwargs.get('pstd', 817)).to_pandas()    #apcpsfc_std
        potato = mloc.series_set.get(pk=kwargs.get('cropf', 1098)).to_pandas()       #Potato 
        px_min = px_mean - px_std
        px_max = px_mean + px_std

        # set negative precipitation values to zero
        p_data[p_data<0] = 0
        px_min[px_min<0] = 0

        # convert series to dataframes with appropriate names
        psi_data = pd.DataFrame({'psi':psi_data})
        ev24_data = pd.DataFrame({'ETm': ev24_data})
        p_data = pd.DataFrame({'P':p_data})
        px_min = pd.DataFrame({'p_min': px_min})
        px_max = pd.DataFrame({'p_max': px_max})
        px_mean = pd.DataFrame({'p_mean': px_mean})
        crop_factor = pd.DataFrame({'Potato': potato})

        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        dtnow = datetime.datetime(yesterday.year,yesterday.month,yesterday.day,tzinfo=pytz.utc)
        filename = 'gift{:%y%m%d}.csv'.format(dtnow)
        response =  waterloo.run(psi_data, ev24_data, p_data, px_mean, px_max, px_min, crop_factor, dtnow = dtnow)
        
        s = StringIO()
        response.to_csv(s)
        result = {filename: s.getvalue()}

        callback = kwargs.get('callback', None)
        if callback is not None:
            callback(result)        

        return result    
    
