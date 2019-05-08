'''
Created on Feb 12, 2014

@author: theo
'''
import os, fnmatch, re
import pytz, datetime
import matplotlib
from django.utils import timezone
from django.utils.translation import ugettext as _
import requests
matplotlib.use('agg')
import matplotlib.pylab as plt
from django.contrib.gis.geos import Point
from django.conf import settings
from matplotlib import rcParams
rcParams['font.size'] = '8'

import logging
logger = logging.getLogger(__name__)

# EPSG codes
RDNEW=28992
RDOLD=28991
WEBMERC=3857
GOOGLE=900913
AMERSFOORT=4289
WGS84=4326

EPOCH = pytz.utc.localize(datetime.datetime(1970,1,1,0,0,0))

def unix_timestamp(dt):
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, pytz.utc)            
    else:
        dt = timezone.localtime(dt,pytz.utc)
    return (dt-EPOCH).total_seconds()

def to_millis(dt):
    ''' conversion of datetime to unix timestamp in milliseconds ''' 
    return int(unix_timestamp(dt)*1000) if isinstance(dt, (datetime.date, datetime.datetime,)) else dt
    
# thumbnail size and resolution
THUMB_DPI=72
THUMB_SIZE=(9,3) # inch

def toGoogle(p):
    return trans(p,GOOGLE)

def toWGS84(p):
    return trans(p,WGS84)

def toRD(p):
    return trans(p,RDNEW)

def trans(p, srid):
    '''transform Point p to requested srid'''
    if not isinstance(p,Point):
        raise TypeError(_('django.contrib.gis.geos.Point expected'))
    if not p.srid:
        p.srid = WGS84
    p.transform(srid)
    return p

def get_address(lon, lat):        
    ''' haal adres gegevens op met google maps geocoding api '''
    url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={key}'.format(lon=lon,lat=lat,key=settings.GOOGLE_MAPS_API_KEY2)
    response = requests.get(url=url)
    response.raise_for_status()
    return response.json()

def save_thumbnail(series,imagefile,kind='line'):
    plt.figure(figsize=THUMB_SIZE,dpi=THUMB_DPI)
    try:
        n = series.count() / (THUMB_SIZE[0]*THUMB_DPI)
        if n > 1:
            #use data thinning: take very nth row
            src = series.iloc[::n]
        else:
            src = series
        options = {'grid': False, 'legend': False}
        if kind == 'column':
            options['xticks'] = []
            src.plot(kind='bar', **options)
        elif kind == 'area':
            x = src.index
            y = src.values
            src.plot(**options)
            plt.fill_between(x,y)
        else:
            src.plot(**options)
        plt.savefig(imagefile,transparent=True)
    except:
        pass
    plt.close()
    
def thumbtag(imagefile):
    url = os.path.join(settings.MEDIA_URL, imagefile)
    return '<a href="%s"><img src="%s" height="60px"/></a>' % (url, url)

def find_files(pattern, root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

# pattern that matches ftp directory listing 
#-rw-rw-r-- 1 theo theo    200796 Mar  4 15:08 acacia.log\r\n
#-rw-rw-r-- 1 theo theo     94222 Mar  4 14:45 django.log\r\n

FTPDIRPATTERN = r'(?P<flags>[drwxst-]{10})\s+(?P<count>\d+)\s+(?P<user>\w+)\s+(?P<group>\w+)\s+(?P<size>\d+)\s+(?P<date>\w{3}\s+\d{1,2}\s+\d{2}:\d{2})\s+(?P<file>[^\r]+)'

def is_dirlist(content):
    return re.search(FTPDIRPATTERN, content) is not None

def get_dirlist(content):
    '''returns ftp directory listing as group dict'''
    return [m.groupdict() for m in re.finditer(FTPDIRPATTERN, content, re.MULTILINE)]

from zipfile import ZipFile
import StringIO
from django.http import HttpResponse
import django.utils.text as dut

def slugify(value):
    return dut.slugify(unicode(value))

def datasources_as_zip(datasources, zipname):
    io = StringIO.StringIO()
    zf = ZipFile(io,'w')
    for d in datasources:
        folder = slugify(d.name)
        for f in d.sourcefiles.all():
            try:
                filepath = f.filepath()
                zippath = os.path.join(folder, f.filename())
                zf.write(filepath,zippath)
            except Exception as e:
                logger.error(_('Cannot add file {} to zip archive: {}').format(f, e))
    zf.close()
    resp = HttpResponse(io.getvalue(), content_type = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zipname
    return resp

def datasource_as_csv(d):
    logger.debug(_('creating csv file for datasource %s') % d.name)
    filename = slugify(d.name) + '.csv'
    csv = d.to_csv()
    logger.debug(_('csv file created, size = %d bytes') % len(csv))
    resp = HttpResponse(csv, content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=%s' % filename
    return resp

def datasource_as_zip(ds):
    return datasources_as_zip([ds],'%s.zip'% slugify(ds.name))
    
def meetlocatie_as_zip(loc):
    return datasources_as_zip(loc.datasources.all(),'%s.zip'% slugify(loc.name))

def series_as_csv(series):
    filename = slugify(series.name) + '.csv'
    csv = series.to_csv()
    resp = HttpResponse(csv, content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=%s' % filename
    return resp

def chart_as_csv(chart):
    filename = slugify(chart.name) + '.csv'
    csv = chart.to_csv(raw=False) # use validated data if possible
    resp = HttpResponse(csv, content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=%s' % filename
    return resp

def resample_rule(delta):
    ''' determine nice Pandas resample rule based on datetime.timedelta '''
    days = delta.days
    rule = ''
    if days > 1:
        if days < 7:
            rule = 'D'
        elif days < 30:
            rule = 'W'
        elif days < 365:
            rule = 'M'
        else:
            rule = 'A'
    else:
        mins = delta.seconds/60
        if mins > 1:
            if mins < 2:
                rule = 'T'
            elif mins < 5:
                rule = '2T'
            elif mins < 10:
                rule = '5T'
            elif mins < 15:
                rule = '10T'
            elif mins < 30:
                rule = '15T'
            elif mins < 60:
                rule = '30T'
            else:
                hours = mins / 60
                if hours < 3:
                    rule = 'H'
                elif hours < 6:
                    rule = '3H'
                elif hours < 12:
                    rule = '6H'
                elif hours < 24:
                    rule = '12H'
                else:
                    rule = 'D'
        else:
            rule = 'S'
    return rule
