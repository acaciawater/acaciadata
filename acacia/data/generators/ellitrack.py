'''
Created on Mar 30, 2017

@author: theo
'''
from acacia.data.generators.generic import GenericCSV
from acacia.data.generators import generator
from acacia.data.util import get_dirlist
import StringIO
logger = generator.logger
from ftplib import FTP
from urlparse import urlparse
from django.utils import timezone
import dateutil

class ElliTrack(GenericCSV):
    def __init__(self,*args,**kwargs):
        kwargs['separator'] = '\\t'
        return super(ElliTrack,self).__init__(*args,**kwargs)
    
    def get_data(self, f, **kwargs):
        data = GenericCSV.get_data(self, f, **kwargs)
        if data is not None:
            if 'Waterstand' in data:
                data['Waterstand'] = data['Waterstand'] / 100
        return data

    def download(self, **kwargs):
 
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
                tz = timezone.get_current_timezone()
                for f in dirlist:
                    if start is not None:
                        date = dateutil.parser.parse(f['date'])
                        date = timezone.make_aware(date,tz)
                        if date < start:
                            continue
                    filename = f['file']
                    urlfile = url + '/' + filename
                    try:
                        f = StringIO.StringIO()
                        ftp.retrbinary('RETR '+ filename, f.write)
                        result[filename] = f.getvalue()
                    except Exception as e:
                        logger.exception('ERROR opening {url}: {reason}'.format(url=urlfile,reason=e))
 
            if callback is not None:
                callback(result)
                 
        return result
