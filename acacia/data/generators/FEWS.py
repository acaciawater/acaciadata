import logging
import pandas as pd
from generator import Generator
import time
import json
import requests
import datetime

import os, urllib2, cgi
import re
import dateutil
import acacia.data.util as util
from django.utils import timezone
from django.core.files.base import File
import pandas as pd

logger = logging.getLogger(__name__)

def spliturl(url):
    pattern = r'^(?P<scheme>ftp|https?)://(?:(?P<user>\w+)?(?::(?P<passwd>\S+))?@)?(?P<url>.+)'
    try:
        m = re.match(pattern, url)
        return m.groups()
    except:
        return ()

# logger = logging.getLogger(__name__)

class FEWS(Generator):
    ''' Get timeseries EC en Chlorisiteit from FEWS'''
#     def download(self):
 
        
    def get_data(self, f, **kwargs):
        timestamps = []
        measurements = []
        datasource = json.load(f)
        timeseries = datasource['events']
        columns = [datasource['name']]
        for t in timeseries:
            timestamps.append(t['timestamp'])
            tmin = t['min']
            tmax = t['min']
            tgem = (tmin+tmax)/2 if (tmin and tmax) else None
            measurements.append(tgem)
        times = [datetime.datetime.fromtimestamp(t/1000.0) for t in timestamps]
        data = pd.DataFrame(measurements,index=times,columns=columns)
        return data
    
    def get_parameters(self, f):
        params = {}
#        content = f.read()
#         datasource = json.loads('"result" :'+content)
        datasource = json.load(f)
        name = datasource['name']
        description = datasource['parameter_referenced_unit']['parameter_short_display_name']
        unit = datasource['parameter_referenced_unit']['referenced_unit_short_display_name']
        params[name] = {'description':description,'unit':unit}
        return params
        
    def download (self, **kwargs):
        '''
        expects credentials, filename_prefix and a timeseries url
        creates or updates bronbestand in json format
        '''
        url =  kwargs.get('url', None)
        if url[-1] != '/':
            url += '/'
            
        if not 'url' in kwargs:
            logger.error('url for download is undefined')
        
        callback = kwargs.get('callback', None)
        username = kwargs.get('username',None)
        passwd = kwargs.get('password',None)
        start = kwargs.get('start',None)
        result = {}
        headers = {'username': username, 'password':passwd}
              
        response = requests.get(url = url, headers = headers)
        data = response.json()
                
        filename = kwargs.get('filename', None) or 'ddsc.json'
        
        if start == None:
            start = data["first_value_timestamp"]
        end = data['last_value_timestamp']
        query = {'start':start, 'end':end}
        response = requests.get(url = url, headers = headers, params=query)
        result[filename] = response.text
        if callback is not None:
            callback(result)        
        return result



