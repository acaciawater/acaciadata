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
    
    #url = 'http://www.knmi.nl/klimatologie/daggegevens/getdata_uur.cgi'
    url = 'http://www.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi'
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
        columns = header['COLUMNS']
        skiprows = self.skiprows if self.engine == 'python' else 0
        data = self.read_csv(f, header=None, names=columns, skiprows = skiprows, skipinitialspace=True, comment = '#', index_col = 1, parse_dates = True)
        return data

    def get_unit(self,descr):
        pat = re.compile(r'\(in\s([^)]+)\)')
        m = re.search(pat,descr)
        if m is not None:
            return m.group(1)[:10]
        else:
            return None

    def get_columns(self, hdr):
        return hdr['COLUMNS'][2:] # eerste 2 zijn station en datum
                
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

class ZipMixin(object):

    def process(self,zipurl,**kwargs):
        ''' modify kwargs to download new zip file using old url '''
        if not 'filename' in kwargs:
            # need unique filename for incremental downloads
            url = kwargs.get('url','')
            filename = 'knmi_meteo'
            if url != '':
                parts = urlparse.urlparse(url)
                path = os.path.basename(os.path.dirname(parts[2]))
                query = urlparse.parse_qs(parts[4])
                
                start = query.get('start',None)
                if isinstance(start,list):
                    start = start[0]
                if start is not None:
                    start = datetime.datetime.strptime(start,'%Y%m%d')
                    kwargs['start'] = start

                stns=query.get('stns',[])
                if stns != []:
                    stn = stns[0]
                    filename = '%s_%s_%s'% (path,filename,stn)
                    kwargs['url'] = self.zipurl.format(stn=stn)
                else:
                    filename = '%s_%s'% (path,filename)
            kwargs['filename'] = filename + '.zip'
        return kwargs
    
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

    zipurl = 'http://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/daggegevens/etmgeg_{stn}.zip'        
    
    def download(self, **kwargs):
        kwargs = self.process(self.zipurl,**kwargs)
        return super(Meteo, self).download(**kwargs)

    def get_header(self, f):
        # new zip files have slightly different format :(
        header = {}
        descr = {}
        header['DESCRIPTION'] = descr
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
        

class UurGegevens(Meteo):
    
    url = 'http://www.knmi.nl/klimatologie/uurgegevens/getdata_uur.cgi'

    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        columns = header['COLUMNS']
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
    
    url = 'http://www.knmi.nl/klimatologie/monv/reeksen/getdata_rr.cgi'

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
        names = header['COLUMNS']
        names.append('NAME')
        skiprows = self.skiprows if self.engine == 'python' else 0
        data = self.read_csv(f, header=None, skiprows = skiprows, names=names, skipinitialspace=True, comment = '#', index_col = 1, parse_dates = True)
        return data

class ZipNeerslag(Neerslag):
    pass

class ZipUurGegevens(UurGegevens):
    pass

