'''
Created on May 31, 2017

@author: theo
'''
import pytz
import datetime
from acacia.data.generators.generator import Generator
import pandas as pd
import dateutil

defurl=r'https://api.buienradar.nl'

try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

class Forecast5(Generator):
    """ Buienradar 5-day forecast with min/max temp and precipitation for Netherlands """
    
    def download(self, **kwargs):
        # format url and pass to generator
        url = kwargs.get('url',defurl)
        kwargs['url'] = url
        if not 'filename' in kwargs:
            today = datetime.date.today()
            kwargs['filename'] = 'br{:%y%m%d}.xml'.format(today)
        return super(Forecast5, self).download(**kwargs)
        
    def get_data(self,fil,**kwargs):
        tree = ET.ElementTree()
        tree.parse(fil)
        root=tree.getroot()
        datum = root.find('.//datum').text
        date = dateutil.parser.parse(datum)
        date = date.replace(hour=0,minute=0,second=0,tzinfo=pytz.utc)
        verwachting = root.find('weergegevens/verwachting_meerdaags')
        data = []
        index = []
        for rain in verwachting.findall('.//minmmregen'):
            date += datetime.timedelta(days=1)
            index.append(date)
            try:
                p = float(rain.text)
            except:
                p = 0
            data.append(p)
        return pd.DataFrame(data, index, columns=['neerslag'])

    def get_parameters(self,fil):
        return {'neerslag': {'description': 'neerslag', 'unit': 'mm/d'},
#                  'tmin': {'description': 'minimum temperatuur', 'unit': 'oC'},
#                  'tmax': {'description': 'maximum temperatuur', 'unit': 'oC'},
                 }

# if __name__ == '__main__':
#     gen = Forecast5()
#     f = '/home/theo/texelmeet/spaarwater/bui.xml'
#     result = gen.get_data(f)
#     print result
