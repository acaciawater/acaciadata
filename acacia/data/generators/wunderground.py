'''
Created on May 31, 2017

@author: theo
'''

defurl=r'http://api.wunderground.com/api/{apikey}/forecast10day/q/{lat},{lon}.json'

debilt=(5.177,52.101)

import datetime, json
from acacia.data.generators.generator import Generator
from django.conf import settings
import pandas as pd

class Forecast10(Generator):
    """ Weather underground 10-day forecast with min/max temp and precipitation """
    
    def download(self, **kwargs):
        # format url and pass to generator
        url = kwargs.get('url',defurl)
        lon,lat = kwargs.get('lonlat',debilt)
        apikey=kwargs.get('key', settings.WUNDERGROUND_APIKEY)
        url = url.format(lat=lat,lon=lon,apikey=apikey)
        kwargs['url'] = url
        if not 'filename' in kwargs:
            kwargs['filename'] = 'wu_{lon:06}{lat:05}.txt'.format(lon=int(lon*1000),lat=int(lat*1000))
        return super(Forecast10, self).download(**kwargs)
        
    def get_data(self,fil,**kwargs):
        resp = json.load(fil)
        index = []
        data = []
        for f in resp['forecast']['simpleforecast']['forecastday']:
            date = f['date']
            d = date['day']
            m = date['month']
            y = date['year']
            index.append(datetime.datetime(y,m,d))
            data.append((f['high']['celsius'],
                        f['low']['celsius'],
                        f['qpf_allday']['mm']))
        return pd.DataFrame.from_records(data, index, columns=['tmin', 'tmax','precip'])

    def get_parameters(self,fil):
        return {'precip': {'description': 'neerslag', 'unit': 'mm/d'},
                 'tmin': {'description': 'minimum temperatuur', 'unit': 'oC'},
                 'tmax': {'description': 'maximum temperatuur', 'unit': 'oC'},
                 }

# import StringIO
# if __name__ == '__main__':
#     gen = Forecast()
#     result = gen.download()
#     for key,contents in result.items():
#         io = StringIO.StringIO(contents)
#         print gen.get_data(io)
#         