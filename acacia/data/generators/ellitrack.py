# -*- coding: utf-8 -*-
'''
Created on Mar 30, 2017

@author: theo
'''
from acacia.data.generators.generic import GenericCSV
from acacia.data.generators import generator
from acacia.data.util import get_dirlist
import StringIO
import pytz
logger = generator.logger
from ftplib import FTP
from urlparse import urlparse, urlunparse
from django.utils import timezone
import dateutil
import pandas as pd

class ElliTrack(GenericCSV):
    
    def get_data(self, f, **kwargs):
        f.seek(0)
        data = pd.read_csv(f, sep='\t', parse_dates = True, index_col = 0, header = self.header, dayfirst = self.dayfirst, decimal = self.decimal, na_values='x')
        self.set_labels(data)
        if not isinstance(data.index,pd.DatetimeIndex):
            # for some reason dateutil.parser.parse not always recognizes valid dates?
            data.drop('None', inplace = True)
            data.index = pd.to_datetime(data.index)
        if data is not None:
            data.dropna(how='all', inplace=True)
            cols = filter(lambda name: name.lower().startswith('waterstand'), data.columns)             
            if len(cols)==1:
                stand=cols[0]
                data[stand] = data[stand] / 100
        return data

#     def get_parameters(self, f):
#         return {'Waterstand' : {'description' : 'Waterstand', 'unit': 'cm' },
#             'Temp_water': {'description' : 'Temperatuur water', 'unit': 'oC' },
#             'Temp_intern': {'description' : 'Temperatuur intern', 'unit': 'oC' }
#         } 
    def get_parameters(self, f):
        f.seek(0)
        data = pd.read_csv(f, sep='\t', nrows=1, parse_dates = True, index_col = 0, header = self.header, dayfirst = self.dayfirst, decimal = self.decimal, na_values='x')
        self.set_labels(data)
        params = {}
        for col in data.columns:
            params[col] = {'description' : col, 'unit': 'm' if 'stand' in col else '°C'}
        return params

    def download1(self, **kwargs):
 
        # Custom FTP download filtering on logger name
        filename = kwargs.get('filename', None)
        content = ''
        start = kwargs.get('start', None)
        callback = kwargs.get('callback', None)
         
        result = {}
        if not 'url' in kwargs:
            logger.error('url for download is undefined')
        else:
            url = kwargs['url']
            parsed = urlparse(url)
            user = kwargs.get('username',None) or parsed.username
            passwd = kwargs.get('password',None) or parsed.password
            scheme = parsed.scheme
            host = parsed.netloc
            port = parsed.port
            path = parsed.path 
            if scheme == 'ftp':
                ftp = FTP()
                ftp.connect(host,port)
                if user:
                    ftp.login(user, passwd)
                if path:
                    ftp.cwd(path)
                mask = 'ElliTrack-'
                logger=kwargs.get('logger',None)
                if logger:
                    mask += logger
                mask += '*'
                
                dirlist = []
                def collect(content):
                    lst = get_dirlist(content)
                    for entry in lst:
                        dirlist.append(entry)
                    
                ftp.dir(mask,collect)
                now = timezone.now()
                for f in dirlist:
                    if start is not None:
                        # directory listing may have date without year. parser assumes current year, may be wrong
                        date = pytz.utc.localize(dateutil.parser.parse(f['date']))
                        if date > now:
                            date = date.replace(year=date.year-1)
                        if date.date() < start.date():
                            continue
                    filename = f['file']
                    urlfile = url + '/' + filename
                    try:
                        io = StringIO.StringIO()
                        ftp.retrbinary('RETR '+ filename, io.write)
                        result[filename] = io.getvalue()
                    except Exception as e:
                        logger.exception('ERROR opening {url}: {reason}'.format(url=urlfile,reason=e))
 
            if callback is not None:
                callback(result)
                 
        return result

    def download(self, **kwargs):
        result = self.download1(**kwargs)
        archive = kwargs.get('archive', False)
        if archive:
            # check archived sub directory
            logger = kwargs.get('logger',None)
            url = kwargs.get('url',None)
            if logger and url:
                import copy        
                parsed = urlparse(url)
                url = urlunparse(parsed._replace(path = parsed.path + '/' + logger))
                options = copy.deepcopy(kwargs)
                options['url'] = url
                options['archive'] = False
                subresult = self.download1(**options)
                result.update(subresult)
        return result
