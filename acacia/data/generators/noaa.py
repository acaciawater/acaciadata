'''
Created on Jan 24, 2014

@author: theo
'''
import datetime, pytz
from pydap.client import open_url
from pydap.exceptions import DapError
from netcdftime import utime
import numpy as np
import pandas as pd
import logging
logger = logging.getLogger(__name__)
from cStringIO import StringIO

from acacia.data.generators.generic import GenericCSV

defurl = 'http://nomads.ncep.noaa.gov:9090/dods/gens/gens{date}/gep_all_{hour}z'
debilt = (5.177,52.101) # lonlat
defvars = ['apcpsfc','tmp2m'] # precipitation and temperature

class GEFS(GenericCSV):

    def get_last_forecast(self,url):

        now = datetime.datetime.now(pytz.utc)
        
        # it takes 5.5 hours before data arrive on GrADS site
        last = now + datetime.timedelta(hours = -6)

        for _ in range(6):
            # forecasts are on h=[0,6,12]
            h = min(int(last.hour/6),2)*6
            last = last.replace(hour = h)
    
            hour = '%02d' % last.hour
            date = now.strftime('%Y%m%d')
            url = url.format(date=date,hour=hour)
            try:
                logger.debug('querying '+url)
                dataset = open_url(url)
                logger.debug('Forecast found for date={date}, hour={hour}'.format(date=date,hour=hour))
                return dataset
            except Exception as e:
                logger.warning('Forecast not found: %s' % e)
                # try previous forecast
                last = last + datetime.timedelta(hours = -6)
        logger.error('No GEFS forecast found')
        return None
    
    def download(self, **kwargs):
        url = kwargs.get('url',defurl)

        dataset = self.get_last_forecast(url)
        if dataset is None:
            return {}

        vars = kwargs.get('vars',defvars)
        
        # convert lonlat to index in grib file (resolution is 1 degree)
        lon,lat = kwargs.get('lonlat',debilt)
        lat = 90 + int(lat)
        lon = int(lon)

        if 'filename' in kwargs:
            filename = kwargs.get('filename')
        else:
            date = datetime.datetime.now().strftime('%Y%m%d%H')
            filename = 'gens{date}_{lon:03}{lat:03}.csv'.format(date=date,lon=lon,lat=lat)
        
        # get conversion to python datetime
        timeunit = dataset.time.attributes['units']
        cdftime = utime(timeunit)

        # download df with ensemnble data for requested variables
        dataframe = None
        for var in vars:
            print var
            grid = dataset[var]
            missing_value = grid.attributes['missing_value']
            ens = grid.ens
            
            # build datetime index
            time = grid.time
            index = [cdftime.num2date(t) for t in time]

            # retrieve data for all ensembles and all timesteps
            data = grid[var][:,:,lat,lon]

            # build pandas dataframe with ensemble data for variable
            df = None
            for i,e in enumerate(ens):
                name=var + str(int(e))
                series = pd.Series(data=[data[i][j][0][0] for j,t in enumerate(time)],index=index,name=name).replace(missing_value,np.nan)
                series[series>1e19] = np.nan
                if df is None:
                    df = pd.DataFrame({name:series},index=index)
                else:
                    df[name] = series

            # compute basic stats
            std = df.std(axis=1)
            mean = df.mean(axis=1)
            if dataframe is None:
                dataframe = pd.DataFrame({var+'_mean': mean, var+'_std': std},index=index)
                dataframe.index.name = 'date'
            else:
                dataframe[var+'_mean'] = mean
                dataframe[var+'_std'] = std
        
        result = {}
        if dataframe is not None:
            buffer = StringIO()
            dataframe.to_csv(buffer)
            result = {filename: buffer.getvalue()}
            if 'callback' in kwargs:
                callback = kwargs['callback']
                callback(result)
        return result

class Pluim(GEFS):
    #pluimvars = ['apcpsfc','tmp2m','tmax2m','tmin2m']
    pluimvars = ['apcpsfc','tmp2m']

    def download(self, **kwargs):
        vars = kwargs.get('vars',self.pluimvars)
        return super(Pluim,self).download(**kwargs)
    
    def get_data(self,fil,**kwargs):
        df1 = super(Pluim,self).get_data(fil,**kwargs)
        df2 = pd.DataFrame({'tmin': df1['tmp2m_mean']-df1['tmp2m_std']-273.15, 
                           'tmp2m': df1['tmp2m_mean']-273.15,
                           'tmax': df1['tmp2m_mean']+df1['tmp2m_std']-273.15,
                           'pmin': df1['apcpsfc_mean']-df1['apcpsfc_std'],
                           'apcpsfc': df1['apcpsfc_mean'],
                           'pmax': df1['apcpsfc_mean']+df1['apcpsfc_std']})
        pmin = df2['pmin']
        pmin[pmin<0] = 0
        return df2

    def get_parameters(self,fil):
        return {
                 'tmin': {'description': 'minimum temperatuur', 'unit': 'oC'},
                 'tmp2m': {'description': 'gemiddelde temperatuur', 'unit': 'oC'},
                 'tmax': {'description': 'maximum temperatuur', 'unit': 'oC'},
                 'tmin': {'description': 'minimum temperatuur', 'unit': 'oC'},
                 'pmin': {'description': 'minimum neerslag', 'unit': 'mm'},
                 'apcpsfc': {'description': 'gemiddelde neerslag', 'unit': 'mm'},
                 'pmax': {'description': 'maximum neerslag', 'unit': 'mm'},
                 }
    
if __name__ == '__main__':
    datafile = r'/home/theo/acaciadata.com/spaarwater/media/spaarwater/borgsweer/perceel-1/datafiles/gefs-borgsweer/gens2016012613_007143.csv'
    pluim = Pluim()
    par = pluim.get_parameters(datafile)
    dat = pluim.get_data(datafile)
    print dat
    
#     gefs = GEFS()
#     result = gefs.download()
