'''
Created on Jan 24, 2014

@author: theo
'''
import logging, re, os
import urlparse
import StringIO
import datetime
import numpy as np
import zipfile

logger = logging.getLogger(__name__)

from generator import Generator

#for incremental downloads downlaoded files are saved with unique name and all files are added to the datasource  
INCREMENTAL_DOWNLOAD = False

class Meteo(Generator):
    ''' Dag waarden van meteostation(s) ophalen '''
    
    url = 'http://projects.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi'
    def download(self, **kwargs):
        if not 'filename' in kwargs:
            # need unique filename for incremental downloads
            url = kwargs.get('url','')
            filename = 'knmi_meteo'
            if url != '':
                parts = urlparse.urlparse(url)
                path = os.path.basename(os.path.dirname(parts[2]))
                query = urlparse.parse_qs(parts[4])
                stns=query.get('stns',[])
                if stns != []:
                    filename = '%s_%s_%s'% (path,filename,stns[0])
                else:
                    filename = '%s_%s'% (path,filename)
            kwargs['filename'] = filename + '.txt'
        return super(Meteo, self).download(**kwargs)
        
    def get_header(self, f):
        header = {}
        descr = {}
        header['DESCRIPTION'] = descr
        header['COLUMNS'] = []
        line = f.readline()
        self.skiprows = 0
        while line != '':
            if line.startswith('# YYYYMMDD'):
                line = f.readline()
                self.skiprows += 1
                while line.startswith('#'):
                    if line.startswith('# STN,YYYYMMDD'):
                        columns = [w.strip() for w in line[2:].split(',')]
                        header['COLUMNS'] = [c for c in columns if len(c)>0]
                    else:
                        eq = line.find('=')
                        if eq>0:
                            key = line[1:eq].strip()
                            val = line[eq+1:].strip()
                            descr[key]=val
                    line = f.readline()
                    self.skiprows += 1
                break
            else:
                line = f.readline()
                self.skiprows += 1
        return header
    
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        columns = header.get('COLUMNS',[])
        skiprows = self.skiprows if self.engine == 'python' else 0
        data = self.read_csv(f.file.file, header=None, names=columns, skiprows = skiprows, skipinitialspace=True, comment = '#', index_col = 1, parse_dates = True)
        return data

    def get_unit(self,descr):
        pat = re.compile(r'\(in\s([^)]+)\)')
        m = re.search(pat,descr)
        if m is not None:
            return m.group(1)[:10]
        else:
            return None

    def get_columns(self, hdr):
        columns = hdr.get('COLUMNS',[])
        return columns[2:] if len(columns)>2 else columns
    
    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = self.get_columns(header)
        desc = header['DESCRIPTION']
        params = {}
        for name in names:
            descr = desc.get(name,name)
            unit = self.get_unit(descr)
            if unit is None:
                unit = 'unknown'
            else:
                rep = '(in %s);' % unit
                descr = descr.replace(rep,'')
            params[name] = {'description' : descr, 'unit': unit}
        return params

def datehour_parser(ymd,hours):
    try:
        return np.array([datetime.datetime.strptime(d,'%Y%m%d') + datetime.timedelta(hours=int(h)) for d,h in zip(ymd,hours)])
    except Exception as e:
        print e    
#    return np.array([datetime.datetime.strptime(a + ('0' if b == '24' else b), '%Y%m%d%H') for a,b in zip(ymd,h)])

class UurGegevens(Meteo):
    
    url = 'http://projects.knmi.nl/klimatologie/uurgegevens/getdata_uur.cgi'

    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        columns = header.get('COLUMNS',[])
        skiprows = self.skiprows # if self.engine == 'python' else 0
        # Bij uurgegevens kan er een carriage return (\r) tussen de kolommen zitten
        with open(f.path,'rb') as f:
            text = f.read().translate(None,'\r')
            io = StringIO.StringIO(text)
            data = self.read_csv(io, 
                                 header=None, 
                                 names=columns, 
                                 skiprows = skiprows, 
                                 skipinitialspace=True, 
                                 comment = '#', 
                                 index_col = 'Datum', 
                                 parse_dates={'Datum': [1,2]}, 
                                 date_parser = datehour_parser)
        return data

    def get_columns(self, hdr):
        return hdr['COLUMNS'][3:] # eerste 3 zijn station, datum en uur

class Neerslag(Meteo):
    '''Dagwaarden van neerslagstations ophalen'''
    
    url = 'http://projects.knmi.nl/klimatologie/monv/reeksen/getdata_rr.cgi'

    def download(self, **kwargs):
        if not 'filename' in kwargs:
            url = kwargs.get('url','')
            filename = 'knmi_neerslag'
            if url != '':
                parts = urlparse.urlparse(url)
                query = urlparse.parse_qs(parts[4])
                stns=query.get('stns',[])
                if stns != []:
                    filename = '%s%s'% (filename,stns[0])
            kwargs['filename'] = filename + '.txt'
        return super(Neerslag, self).download(**kwargs)
    
    def get_header(self, f):
        header = {}
        descr = {}
        header['DESCRIPTION'] = descr
        header['COLUMNS'] = []
        self.skiprows = 0
        for i in range(0,9):
            line = f.readline()
            self.skiprows += 1
        lastkey = ''
        while line != '':
            if line.strip() == '':
                line = f.readline()
                self.skiprows += 1
                break
            key = line[:9].strip()
            if len(key) > 0:
                descr[key] = line[11:].strip()
                lastkey = key
            else:
                key = lastkey
                descr[key] = descr[key] + line[11:].strip()
            line = f.readline()
            self.skiprows += 1
            
        while line != '':
            if line.startswith('STN,YYYYMMDD'):
                columns = [w.strip() for w in line.split(',')]
                header['COLUMNS'] = [c for c in columns if len(c)>0]
                break
            else:
                line = f.readline()
                self.skiprows += 1
        return header

    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        names = header.get('COLUMNS',[])
        names.append('NAME')
        skiprows = self.skiprows if self.engine == 'python' else 0
        data = self.read_csv(f.file.file, header=None, skiprows = skiprows, names=names, skipinitialspace=True, comment = '#', index_col = 1, parse_dates = True)
        return data

class ZipMixin(object):
    
    def unzip(self, fil):
        try:
            with zipfile.ZipFile(fil,'r') as z:
                for name in z.namelist():
                    # first (and only) file in zip archive
                    return z.open(name)
        except zipfile.BadZipfile:
            # maybe not a zip file after all?
            return fil

  
class ZipMeteo(Meteo,ZipMixin):

    def download(self,**kwargs):
        if not 'filename' in kwargs:
            # need unique filename for incremental downloads
            url = kwargs.get('url','')
            filename = 'etmgeg_000.zip'
            if url != '':
                parts = urlparse.urlparse(url)
                filename = os.path.basename(os.path.basename(parts[2]))
            kwargs['filename'] = filename
        return Generator.download(self,**kwargs)
    
    def get_header(self, f):
        # new zip files have slightly different format :(
        header = {}
        descr = {}
        header['DESCRIPTION'] = descr
        header['COLUMNS'] = []
        line = f.readline()
        self.skiprows = 0
        while line != '':
            if line.startswith('YYYYMMDD'):
                line = f.readline()
                self.skiprows += 1
                while len(line)>1:
                    eq = line.find('=')
                    if eq>0:
                        key = line[:eq].strip()
                        val = line[eq+1:].strip()
                        descr[key]=val
                    else:
                        break
                    line = f.readline()
                    self.skiprows += 1
                while not line.startswith('# STN,YYYYMMDD'):
                    line = f.readline()
                    self.skiprows += 1
                columns = [w.strip() for w in line[2:].split(',')]
                header['COLUMNS'] = [c for c in columns if len(c)>0]
                line = f.readline()
                self.skiprows += 1
                break
            else:
                line = f.readline()
                self.skiprows += 1
        return header

    def get_parameters(self, fil):
        return super(ZipMeteo,self).get_parameters(self.unzip(fil))

    def get_data(self, f, **kwargs):
        return super(ZipMeteo,self).get_data(self.unzip(f),**kwargs)
        
class ZipNeerslag(Neerslag, ZipMixin):
    
    def download(self,**kwargs):
        if not 'filename' in kwargs:
            # need unique filename for incremental downloads
            url = kwargs.get('url','')
            filename = 'neerslaggeg_000.zip'
            if url != '':
                parts = urlparse.urlparse(url)
                filename = os.path.basename(os.path.basename(parts[2]))
            kwargs['filename'] = filename
        return Generator.download(self,**kwargs)

    def get_parameters(self, fil):
        return super(ZipNeerslag,self).get_parameters(self.unzip(fil))

    def get_data(self, f, **kwargs):
        return super(ZipNeerslag,self).get_data(self.unzip(f),**kwargs)

class ZipUurGegevens(ZipMeteo):

    def get_columns(self, hdr):
        columns = hdr.get('COLUMNS',[])
        return columns[3:] if len(columns)>3 else columns  # eerste 3 zijn station, datum en uur

    def get_data(self, f, **kwargs):
        f=self.unzip(f)
        header = self.get_header(f)
        columns = header.get('COLUMNS',[])
        skiprows = self.skiprows # if self.engine == 'python' else 0
        text = f.read().translate(None,'\r')
        io = StringIO.StringIO(text)
        data = self.read_csv(io, 
                             header=None, 
                             names=columns, 
                             skiprows = skiprows, 
                             skipinitialspace=True, 
                             comment = '#', 
                             index_col = 'Datum', 
                             parse_dates={'Datum': [1,2]}, 
                             date_parser = datehour_parser)
        return data

class Radar(Generator):
    defurl = 'ftp://data.knmi.nl/download/radar_corr_accum_24h/1.0/noversion/{year}/{month}/{day}'

    def download(self, **kwargs):
        url = kwargs.get('url', self.defurl)
        url = url.format(year=2017,month=5,day=14)
        kwargs['url']=url
        if not 'filename' in kwargs:
            kwargs['filename'] = 'rad24h20170515'
        return Generator.download(self, **kwargs)
    
# # KNMI neerslagradar
# from pydap.client import open_url
# from pydap.exceptions import DapError
# import pytz
# import osr, gdal
# import numpy.ma as ma
# import pandas as pd
# 
# UTC = pytz.utc
# UTC2000 = UTC.localize(datetime.datetime(2000, 1, 1))
# 
# def thredds():
#     url = 'http://opendap.knmi.nl/knmi/thredds/dodsC/radarprecipclim/RAD_NL25_RAC_MFBS_24H_NC.nc'
#     dataset = open_url(url)
#     print dataset.keys()
#     grid = dataset.image1_image_data
#     print grid.dimensions, grid.shape
#     geo = dataset.geographic
#     print geo.attributes
#     projection = dataset.projection
#     print projection.attributes
#     
#     #corners = geo.attributes['geo_product_corners']
#     rowoffset = geo.attributes['geo_row_offset']
#     proj4 = projection.attributes['proj4_origin']
#     crs = osr.SpatialReference()
#     crs.ImportFromProj4(proj4)
#     wgs84 = osr.SpatialReference()
#     wgs84.ImportFromEPSG(4326)
#     trans = osr.CoordinateTransformation(wgs84, crs)
#     
# #     sw = corners[0:2]
# #     nw = corners[2:4]
# #     ne = corners[4:6]
# #     se = corners[6:]
# #     pt1 = trans.TransformPoint(sw[0],sw[1],0)
# #     pt2 = trans.TransformPoint(nw[0],nw[1],0)
# #     pt3 = trans.TransformPoint(ne[0],ne[1],0)
# #     pt4 = trans.TransformPoint(se[0],se[1],0)
# #     dx1 = pt3[0] - pt2[0]
# #     dx2 = pt4[0] - pt1[0]
# #     dy1 = pt2[1] - pt1[1]
# #     dy2 = pt3[1] - pt4[1]
# #     print dx1, dx2, dy1, dy2
# #     print proj4
# #     print corners
#     
#     p=(5.177,52.101) # de bilt
#     p=trans.TransformPoint(p[0],p[1])
#     col = int(p[0])
#     row = -int(p[1]+rowoffset)
# 
#     time = dataset.time[:]
#     t = [UTC2000 + datetime.timedelta(seconds=float(s)) for s in time]
#     t1 = len(t)-10
#     print t[-1]
#     z = grid[t1,row,col].flatten()
#     z = ma.masked_where(z == -9999.0, z)
#     data = pd.Series(z,index=t)
#     data.index.name = 'Datum'
#     data.name = 'Neerslag'
#     io = StringIO.StringIO()
#     data.to_csv(io,header=True)
#     response = io.getvalue()
# 
# def hdf(fname):
#     fname = '/media/sf_C_DRIVE/Users/theo/Documents/RAD_NL25_RAC_24H_201705150800.h5'
#     hdf = gdal.OpenShared(fname)
#     
#     meta = hdf.GetMetadata()
#     proj4 = meta['geographic_map_projection_projection_proj4_params']
#     rowoffset = float(meta['geographic_geo_row_offset'])
#     crs = osr.SpatialReference()
#     crs.ImportFromProj4(proj4)
#     wgs84 = osr.SpatialReference()
#     wgs84.ImportFromEPSG(4326)
#     trans = osr.CoordinateTransformation(wgs84, crs)
# 
#     sets = hdf.GetMetadata('SUBDATASETS')
#     image1 = gdal.OpenShared(sets['SUBDATASET_1_NAME'])
#     image2 = gdal.OpenShared(sets['SUBDATASET_2_NAME'])
# 
#     p=(5.177,52.101) # de bilt
#     p=trans.TransformPoint(p[0],p[1])
#     col = int(p[0])
#     row = -int(p[1]+rowoffset)
# 
#     band1 = image1.GetRasterBand(1)
#     z1 = band1.ReadAsArray(col, row, 1, 1)[0][0]
#     band2 = image1.GetRasterBand(1)
#     z2 = band2.ReadAsArray(col, row, 1, 1)[0][0]
#     return (z1, z2)
#     
# if __name__ == '__main__':
#     thredds()
# 
# #     fname = '/media/sf_C_DRIVE/Users/theo/Documents/RAD_NL25_RAC_24H_201705150800.h5'
# #     z = hdf(fname)
# #     print z
