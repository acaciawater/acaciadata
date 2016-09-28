'''
Created on Nov 13, 2015

@author: theo
'''

import logging, re, zipfile, csv, datetime, dateutil, StringIO
from acacia.data.generators.generator import Generator

import pandas as pd
import numpy as np
import pytz
import json
import csv

logger = logging.getLogger(__name__)

def convdate(txt,tz=None):
    try:
        dt = datetime.datetime.strptime(txt,'%d-%m-%Y')
        if tz is not None:
            dt = dt.replace(tzinfo=tz)
        return dt
    except:
        return None

def convtime(txt,tz=None):
    try:
        dt = datetime.datetime.strptime(txt,'%d-%m-%Y %H:%M')
        if tz is not None:
            dt = dt.replace(tzinfo=tz)
        return dt
    except:
        return None

def date_parser(dt):
    ''' date parser for pandas read_csv '''
    tz = pytz.timezone('CET')
    return np.array([convdate(t,tz) for t in dt])

def time_parser(t):
    ''' datetime parser for pandas read_csv '''
    tz = pytz.timezone('CET')
    return convtime(t,tz)
#WB_URL = r'http://live.waterbase.nl/wswaterbase/cgi-bin/wbGETDATA?site=MIV&lang=nl&ggt=id2392&loc=GENMDN&from=201001010000&to=201012312359&fmt=html'
#WB_URL = r'http://live.waterbase.nl/wswaterbase/cgi-bin/wbGETDATA?site=MIV&lang=nl&ggt=id1&loc=CULBBG&from=201301010000&to=201512312359'
WB_URL = r'http://live.waterbase.nl/wswaterbase/cgi-bin/wbGETDATA?site=MIV&lang=nl&ggt=id{id}&loc={loc}&from={start}&to={stop}'

class Waterbase(Generator): # waterstanden van waterbase
    def __init__(self, *args, **kwargs):
        super(Waterbase,self).__init__(*args,**kwargs)

    def download(self,**kwargs):
        loc = kwargs.get('locatie', 'CULBBG')
        id = kwargs.get('id', 1) # id1 = waterhoogte, id2392 = 
        start = kwargs.get('start', '201601010000')
        stop = kwargs.get('stop', '201612312359')
        url = kwargs.get('url', WB_URL)
        url = url.format(loc=loc,id=id,start=start,stop=stop)
        kwargs['url'] = url
        return super(Waterbase, self).download(**kwargs)

    def _get_parameter(self,row):
        wns = row['waarnemingssoort']
        name = wns.split()[0]
        return {'name':name, 'description': wns, 'unit': row['eenheid']}
            
    def get_parameters(self, f):
        f.seek(0)
        data = self.read_csv(f, parse_dates = {'Datumtijd': ['datum', 'tijd']}, index_col = 'Datumtijd', skiprows = 3, sep =';', 
                             usecols = ['datum', 'tijd', 'waarde', 'waarnemingssoort', 'eenheid'], nrows = 1)
        row = data.iloc[0]
        p = self._get_parameter(row)
        return {p['name']: {'description': p['description'], 'unit': p['unit']}}

    def get_data(self, f, **kwargs):
        f.seek(0)
        data = self.read_csv(f, parse_dates = {'Datumtijd': ['datum', 'tijd']}, index_col = 'Datumtijd', skiprows = 3, sep =';', 
                             usecols = ['datum', 'tijd', 'waarde', 'waarnemingssoort', 'eenheid'])
        if not isinstance(data.index,pd.DatetimeIndex):
            # for some reason dateutil.parser.parse not always recognizes valid dates?
            data.drop('None', inplace = True)
            data.index = pd.to_datetime(data.index)
        data.dropna(how='all', inplace=True)
        p = self._get_parameter(data.iloc[0])
        data.drop('waarnemingssoort',axis=1,inplace=True)
        data.drop('eenheid',axis=1,inplace=True)
        data.columns = [p['name']]
        return data

class RWSHistory(Generator):
    
    def get_header(self, f):
        header = {}
        descr = {}
        header['DESCRIPTION'] = descr
        header['COLUMNS'] = ['Datum']
        f.seek(0)
        line = f.readline()
        self.skiprows = 0
        self.hastime = False
        while line != '':
            if re.match('^\d{2}\-\d{2}\-\d{4}\s+\d{2}\:\d{2}',line):
                self.hastime = True
                header['COLUMNS'].insert(1,'Tijd')
                break
            elif re.match('^\d{2}\-\d{2}\-\d{4}',line):
                break
            colon = line.find(':')
            if colon>0:
                key = line[:colon].strip()
                val = line[colon+1:].strip()
                descr[key]=val
                if key == 'Parameter':
                    header['COLUMNS'].append(val[:15].strip())
            line = f.readline()
            self.skiprows += 1
        return header
    
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        columns = header.get('COLUMNS',[])
        f.seek(0)
        skiprows = self.skiprows
        buf = StringIO.StringIO(f.read())
        if self.hastime:
            data = self.read_csv(buf, header=None, names=columns, sep = r'\s+', skiprows = skiprows, index_col = 'DatumTijd', parse_dates = {'DatumTijd': [0,1]}, date_parser = time_parser, na_values=-999)
        else:
            data = self.read_csv(buf, header=None, names=columns, sep = r'\s+', skiprows = skiprows, index_col = 'Datum', parse_dates = True, date_parser = date_parser, na_values=-999)
        return data

    def get_columns(self, hdr):
        cols = hdr.get('COLUMNS',[])
        return [cols[-1]]
    
    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = self.get_columns(header)
        data = header['DESCRIPTION']
        params = {}
        for name in names:
            # there is only 1 parameter
            unit = data['Eenheid']
            descr = data['Parameter'][16:]
            params[name] = {'description' : descr, 'unit': unit}
        return params

#LMW_URL = r'http://www.rijkswaterstaat.nl/apps/geoservices/rwsnl/awd.php?mode=data&loc=LITB&net=LMW&projecttype=watertemperatuur&category=1'
LMW_URL = r'http://www.rijkswaterstaat.nl/apps/geoservices/rwsnl/awd.php?mode=data&loc={loc}&net=LMW&projecttype={parameter}&category=1'

class LMW(Generator):
    # json bestand met 10 minuten metingen van Landelijk Meetnet Water

    jsonobj = None

    def download(self, **kwargs):
        url = kwargs.get('url', LMW_URL)
        parameter = kwargs.get('parameter','watertemperatuur') 
        locatie = kwargs.get('locatie', 'LITB')
        if not 'filename' in kwargs:
            kwargs['filename'] = 'lmw_{}_{}.json'.format(locatie, parameter)
        kwargs['url'] = url.format(loc=locatie, parameter=parameter)
        return super(LMW, self).download(**kwargs)

    def get_data1(self, fil, **kwargs):
        try:
            # assume 1 series per file
            # can be H10 (Water levels) and H10V (forecaste waterlevels)
            fil.seek(0)
            obj=json.load(fil)
            tz = pytz.timezone('CET')
            series = None
            series_name = obj.keys()[0]
            for k,v in obj.items():
                index = [datetime.datetime.fromtimestamp(int(x['tijd']),tz) for x in v]
                def conv(x):
                    try:
                        return float(x)
                    except:
                        return None
                values = [conv(x['waarde']) for x in v]
                s = pd.Series(index=index,data=values)
                if series is None:
                    series = s
                else:
                    series = series.append(s)
        except Exception as e:
            raise e
#            logger.exception('Error parsing json response')
        return pd.DataFrame({series_name: series})

    def get_data(self, fil, **kwargs):
        try:
            fil.seek(0)
            obj=json.load(fil)
            tz = pytz.timezone('CET')
            dfs = []
            for k,v in obj.items():
                index = [datetime.datetime.fromtimestamp(int(x['tijd']),tz) for x in v]
                def conv(x):
                    try:
                        return float(x)
                    except:
                        return None
                values = [conv(x['waarde']) for x in v]
                s = pd.Series(index=index,data=values)
                dfs.append(pd.DataFrame({k:s}))
        except Exception as e:
            raise e
#            logger.exception('Error parsing json response')
        return pd.concat(dfs).sort()
        
    def get_parameters(self, fil):
        try:
            fil.seek(0)
            obj=json.load(fil)
            params = {}
            for k,v in obj.items():
                params[k] = {'description' : v[0]['parameternaam'], 'unit': ''}
        except:
            logger.exception('Error parsing json response')
        return params

class LMW10(Generator):
    # zip bestand met 10 minuten metingen van Landelijk Meetnet Water (https://www.rijkswaterstaat.nl/rws/opendata/meetdata/meetdata.zip)
    def __init__(self,*args,**kwargs):
        super(LMW10,self).__init__(*args,**kwargs)
        self.parameter = kwargs.get('parameter','H10') 
        self.locatie = kwargs.get('locatie', 'AMRO')
        self.index = -1 # row number in file
        
    def download(self, **kwargs):
        kwargs['filename'] = 'meetdata.zip'
        return super(LMW10, self).download(**kwargs)
        
    def get_header(self, fil):
        header = {}
        descr = {}
        cols = []
        header['DESCRIPTION'] = descr
        header['COLUMNS'] = cols
        with zipfile.ZipFile(fil,'r') as z:
            with z.open('update.adm') as f:
                reader = csv.reader(f,delimiter=',')
                index=-1
                for row in reader:
                    index+=1
                    row = [r.strip() for r in row]
                    if self.locatie == row[1] and self.parameter == row[3]:
                        keys = ['meetnet_id','locatie_code','leeg','parameter_code','locatie','parameter','unit','from_date', 'to_date', 'format']
                        descr[self.parameter] = dict(zip(keys,row))
                        cols.append(self.parameter)
                        break
                self.skiprows = index
        return header
        
    def get_data(self, fil, **kwargs):
        if 'parameter' in kwargs:
            self.parameter = kwargs['parameter'] 
        if 'locatie' in kwargs:
            self.locatie = kwargs['locatie']
        header = self.get_header(fil)
        descr = header['DESCRIPTION'][self.parameter]
        
        fromDate = descr['from_date']
        fromDate = dateutil.parser.parse(fromDate)
        
        toDate = descr['to_date']
        toDate = dateutil.parser.parse(toDate)

        with zipfile.ZipFile(fil,'r') as z:
            with z.open('update.dat') as f:
                reader = csv.reader(f,delimiter=',')
                for _ in range(self.skiprows):
                    reader.next()
                row = reader.next()
                date = fromDate
                data = []
                index = []
                for d in row:
                    try:
                        d = float(d)
                        if d < -990:
                            d = None
                    except:
                        d = None
                    data.append(d)
                    index.append(date)
                    date = date + datetime.timedelta(minutes=10)
        return pd.DataFrame(index=index, data={self.parameter:data}) 
    
    def get_parameters(self, fil):
        header = self.get_header(fil)
        cols = header['COLUMNS']
        desc = header['DESCRIPTION']
        params = {}
        for colname in cols:
            data = desc[colname]
            unit = data['unit']
            descr = '{param} {loc}'.format(param=data['parameter'],loc=data['locatie'])
            params[colname] = {'description' : descr, 'unit': unit}
        return params
    
if __name__ == '__main__':
    
#     gen = RWSHistory()
#     with open(r'/media/sf_F_DRIVE/acaciadata.com/nederrijnlekenwaal/habe.txt') as f:
#         print gen.get_parameters(f)
#         print gen.get_data(f)
        
#    gen = LMW10()
#    datafile = r'/media/sf_F_DRIVE/acaciadata.com/meetdata.zip'
#   print gen.get_parameters(datafile)
#    print gen.get_data(datafile)
            
    gen = LMW()
    datafile = r'/media/sf_F_DRIVE/acaciadata.com/H10.txt'
    with open(datafile) as f:
        print gen.get_parameters(f)
        print gen.get_data(f)
            
#     gen = Waterbase()
#     datafile = r'/media/sf_F_DRIVE/acaciadata.com/id1-CULBBG-201301010000-201512312359.txt'
#     with open(datafile) as f:
#         print gen.get_parameters(f)
#         print gen.get_data(f)
   