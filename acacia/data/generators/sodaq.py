'''
Created on Feb 16, 2016

@author: theo
'''
import logging, os, pytz, datetime
from urlparse import urlsplit
from acacia.data.generators.generic import GenericCSV
from acacia.mqtt.models import Host, Topic
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def date_parser(ts):
    tz = pytz.timezone('Europe/Amsterdam')
    return np.array([datetime.datetime.fromtimestamp(int(t),tz) for t in ts])

class ECSensor(GenericCSV):
    ''' Continuous EC sensor using MQTT protocol '''

    cols = ['timestamp', 'EC', 'temp', 'temp1', 'temp2', 'pressure', 'humidity', 'battery']
    units = ['sec', 'uS/cm', 'oC', 'oC', 'oC', 'hPa', '%', 'mV']

    def download(self, **kwargs):
        ''' downloads topic messages from database as csv '''
        if not 'url' in kwargs:
            raise ValueError('url is missing')
        try:
            url = urlsplit(kwargs['url'])
        except:
            logger.error('Bad url: '+kwargs['url'])
            return None
        try:
            host = Host.objects.get(host=url.netloc)
            topic = host.topic_set.get(topic=url.path[1:])
            filename = os.path.basename(url.path) + '.csv'
            content = ','.join(self.cols) + '\n'
            content += '\n'.join([m.payload for m in topic.message_set.all()])
            result = {filename: content}
            
            callback = kwargs.get('callback', None)
            if callback is not None:
                callback(result)

            return result
            
        except Host.DoesNotExist:
            logger.error('Host not registered: %' % url.netloc)
        except Topic.DoesNotExist:
            logger.error('Topic not registered: %' % url.path)
        return None

    def get_data(self, f, **kwargs):
        f.seek(0)
        data = self.read_csv(f, parse_dates = [0], index_col = 0, date_parser = date_parser, header = self.header)
        if not isinstance(data.index,pd.DatetimeIndex):
            # for some reason dateutil.parser.parse not always recognizes valid dates?
            data.drop('None', inplace = True)
            data.index = pd.to_datetime(data.index)
        data.dropna(how='all', inplace=True)
        # add column with EC at 25 oC
        data['EC25'] = 1e6 / data['EC'] * (1.0 - 0.02 * (data['temp']-25.0)) 
        return data

    def get_parameters(self, f):
        params = super(ECSensor, self).get_parameters(f)
        params['EC25'] = {'description': 'EC 25oC', 'unit': 'uS/cm' }
        return params
        
if __name__ == '__main__' :
    gen = ECSensor()
    result = gen.download(url='http://vps01.m2m4all.com/EC/Wellen/82f82cac5d1f58ae')
    for filename, content in result.items():
        with open(filename,'w') as f:
            f.write(content)
        with open(filename) as f:
            df = gen.get_data(f)
            print df
            