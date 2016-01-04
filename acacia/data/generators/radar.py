'''
Created on Jan 24, 2014

@author: theo
'''
import pytz
import datetime
import numpy.ma as ma
import pandas as  pd
import StringIO
from pydap.client import open_url
from pydap.exceptions import DapError

import logging
logger = logging.getLogger(__name__)

from generator import Generator
UTC = pytz.utc
UTC2000 = UTC.localize(datetime.datetime(2000, 1, 1))
INCREMENTAL_DOWNLOAD = False

class Regenradar(Generator):
    ''' dagtotalen ophalen van nationale regenradar'''
    def __init__(self, *args, **kwargs):
        super(Regenradar,self).__init__(*args, **kwargs)
        self.url = 'http://opendap.nationaleregenradar.nl/thredds/dodsC/radar/TF2400_A/2000/01/01/RAD_TF2400_A_20000101000000.h5'
        self.x = 0.0
        self.y = 0.0
        self.start = datetime.date(2015,1,1)
        self.stop = datetime.date.today()
        self.init(**kwargs)

    def init(self,**kwargs):
        if 'x' in kwargs:
            self.x = float(kwargs['x'])
        if 'y' in kwargs:
            self.y = float(kwargs['y'])
        if INCREMENTAL_DOWNLOAD:
            # use start/top values
            if 'start' in kwargs:
                d = kwargs['start']
                if hasattr(d,'date'):
                    d = d.date()
                self.start = d
            if 'stop' in kwargs:
                d = kwargs['stop']
                if hasattr(d,'date'):
                    d = d.date()
                self.stop = d
        
    def download(self, **kwargs):
        self.init(**kwargs)
        
        callback = kwargs.get('callback', None)
        url = kwargs.get('url',None) or self.url
        try:
            dataset = open_url(url)
        except Exception as e:
            logger.exception('ERROR opening OpenDAP dataset %s: %s' % (url, e))
            return []
        grid = dataset.precipitation
        data = grid.precipitation
        x0 = dataset.east[0][0]
        y0 = dataset.north[0][0]
            
        col = int((self.x - x0) / 1000)
        row = int((y0 - self.y) / 1000)
        
        time = dataset.time[:]
        t = [UTC2000 + datetime.timedelta(seconds=float(s)) for s in time]
        t1 = -1
        t2 = len(t)-1
        for index,item in enumerate(t):
            date = item.date()
            if t1 < 0 and date >= self.start:
                t1 = index
            if date >= self.stop:
                t2 = index
                break
        z = data[row,col,t1:t2].flatten()
        t = t[t1:t2]
        z = ma.masked_where(z == -9999.0, z)
        data = pd.Series(z,index=t)
        data.index.name = 'Datum'
        data.name = 'Neerslag'
        io = StringIO.StringIO()
        data.to_csv(io,header=True)
        response = io.getvalue()
        t = t[-1]
        if INCREMENTAL_DOWNLOAD:
            # need unique filename if we want to keep all the parts
            filename = 'p%d-%d-%s.csv' % (self.x,self.y,t.strftime('%y%m%d%H%M'))
        else:
            filename = 'rad_tf2400.csv'
        result = [{filename: response},]
        if callback is not None:
            callback(result)
        
        return result

    def get_data(self,fil,**kwargs):
        data = self.read_csv(fil, index_col = 0, parse_dates = True)
        return data

    def get_parameters(self, fil):
        return  dict({'Neerslag': {'description' : 'dagelijkse neerslag', 'unit': 'mm/d'}})  

''' from lizard neerslagradar
def values(self, identifier, start_date, end_date):
        # get coordinates for rasterstorequery
        cell_x, cell_y = identifier['google_coords']
        # transform datetimes for rasterstorequery
        format_ = "%Y-%m-%dT%H:%M:%SZ"
        end_date_str = datetime.datetime.strftime(end_date, format_)
        start_date_str = datetime.datetime.strftime(start_date, format_)
        # rasterstore query
        url_template = ('https://raster.lizard.net/data?request=getdata&geom='
               'POINT({x}+{y})&layer=radar:5min&sr=EPSG:3857&start={start}&'
               'stop={stop}&time=1&indent=2')
        url = url_template.format(x=cell_x, y=cell_y, start=start_date_str,
                   stop=end_date_str)
        url_file = urllib2.urlopen(url)
        rasterstore_values = json.load(url_file)

        # transform rasterstore values into required datastructure with dicts
        # in some cases rasterstore contains None values, these are set to 0
        rain_data = rasterstore_values['values']
        rain_datetimes = rasterstore_values['time']
        values = [self._rain_dict(rain_datetimes[i], val if val else 0)
                  for i, val in enumerate(rain_data)]
        return values
'''

import urllib2,json 

def lizard_radar(cell_x, cell_y, start_date, end_date):
        # transform datetimes for rasterstorequery
        format_ = "%Y-%m-%dT%H:%M:%SZ"
        end_date_str = datetime.datetime.strftime(end_date, format_)
        start_date_str = datetime.datetime.strftime(start_date, format_)

        # rasterstore query
        url_template = ('https://raster.lizard.net/data?request=getdata&geom='
               'POINT({x}+{y})&layer=radar:5min&sr=EPSG:3857&start={start}&'
               'stop={stop}&time=1&indent=2')
        url = url_template.format(x=cell_x, y=cell_y, start=start_date_str,
                   stop=end_date_str)
        url_file = urllib2.urlopen(url)
        rasterstore_values = json.load(url_file)

        # transform rasterstore values into required datastructure with dicts
        # in some cases rasterstore contains None values, these are set to 0
        rain_data = rasterstore_values['values']
        rain_datetimes = rasterstore_values['time']
        return zip(rain_datetimes, rain_data)

DEBILT1 = (5.27542,52.13371)
DEBILT = (587257.028,6824338.265) # google
    
# Lizard neerslagradar
if __name__ == '__main__':
    result = lizard_radar(DEBILT[0],DEBILT[1],datetime.datetime(2015,1,1),datetime.datetime(2015,2,1))
    
# KNMI neerslagradar
# if __name__ == '__main__':
#     url = 'http://opendap.knmi.nl/knmi/thredds/dodsC/radarprecipclim/RAD_NL25_RAC_MFBS_24H_NC/RAD_NL25_RAC_MFBS_24H_8UT_2015_NETCDF.zip'
#     dataset = open_url(url)
#     print dataset.keys()
#     grid = dataset.image1_image_data
#     print grid.dimensions, grid.shape
#     data = grid
#     x0 = dataset.x[0][0]
#     y0 = dataset.y[0][0]
#         
#     col = 350
#     row = 350
#     
#     time = dataset.time[:]
#     t = [UTC2000 + datetime.timedelta(seconds=float(s)) for s in time]
#     t1 = 0
#     t2 = 100
#     z = data[row,col,t1:t2].flatten()
#     z = ma.masked_where(z == -9999.0, z)
#     data = pd.Series(z,index=t)
#     data.index.name = 'Datum'
#     data.name = 'Neerslag'
#     io = StringIO.StringIO()
#     data.to_csv(io,header=True)
#     response = io.getvalue()
