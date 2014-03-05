'''
Created on Feb 12, 2014

@author: theo
'''
import os, fnmatch, re
import matplotlib.pyplot as plt
from django.contrib.gis.gdal.srs import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point
from matplotlib import rcParams
rcParams['font.size'] = '8'

# EPSG codes
RDNEW=28992
RDOLD=28991
WEBMERC=3857
GOOGLE=900913
AMERSFOORT=4289
WGS84=4326

def toGoogle(p):
    return trans(p,GOOGLE)

def toWGS84(p):
    return trans(p,WGS84)

def toRD(p):
    return trans(p,RDNEW)

def trans(p, srid):
    '''transform Point p to requested srid'''
    if  not isinstance(p,Point):
        raise TypeError('django.contrib.gis.geos.Point expected')
    psrid = p.srid
    if not psrid:
        psrid = WGS84
    if (psrid != srid): 
        tr = CoordTransform(SpatialReference(p.srid), SpatialReference(srid))
        p.transform(tr)
    
    return p

def save_thumbnail(series,imagefile,kind='line'):
    plt.figure()
    options = {'figsize': (9,3), 'grid': False, 'xticks': [], 'legend': False}
    if kind == 'column':
        series.plot(kind='bar', **options)
    elif kind == 'area':
        x = series.index
        y = series.values
        series.plot(**options)
        plt.fill_between(x,y)
    else:
        series.plot(**options)
    plt.savefig(imagefile,transparent=True)
    plt.close()
    
def thumbtag(imagefile):
    url = "/media/%s" % imagefile
    return '<a href="%s"><img src="%s" height="60px"\></a>' % (url, url)

def find_files(pattern, root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

# pattern that matches ftp directory listing 
#-rw-rw-r-- 1 theo theo    200796 Mar  4 15:08 acacia.log\r\n\
#-rw-rw-r-- 1 theo theo     94222 Mar  4 14:45 django.log\r\n\

FTPDIRPATTERN = r'(?P<flags>[drwxst-]{10})\s+(?P<count>\d+)\s+(?P<user>\w+)\s+(?P<group>\w+)\s+(?P<size>\d+)\s+(?P<date>\w{3}\s+\d{1,2}\s+\d{2}:\d{2})\s+(?P<file>[^\r]+)'

def is_dirlist(content):
    return re.search(FTPDIRPATTERN, content) is not None

def get_dirlist(content):
    '''returns ftp directory listing as group dict'''
    return [m.groupdict() for m in re.finditer(FTPDIRPATTERN, content, re.MULTILINE)]
        