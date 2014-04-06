import numpy as np
import pandas as pd
import cgi, urllib, urllib2
import xlrd
import datetime, time
import logging
import StringIO
import pytz

from acacia import settings

logger = logging.getLogger(__name__)

from generator import Generator
from acacia.data import __version__

class DecagonException(Exception):
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return 'Decagon Dataservice: %s' % (self.value)

class DataTrac(Generator):
    ''' Generate series from excel table exported by DataTrac '''
            
    def get_data(self, f, **kwargs):
        data = pd.read_excel(f, sheetname='Processed', header=2, index_col=[0], parse_dates = [0], na_values = ['***',])
        #remove units from column names
        data.rename(columns = lambda col: col[len(col.split()[0]):].strip(),inplace=True)
        return data

    def get_parameters(self, f):
        wb = xlrd.open_workbook(file_contents = f.read())
        sheet = wb.sheet_by_name('Processed')
        params = {}
        row = sheet.row(2)
        for col in row[1:]:
            unit = col.value.split()[0]
            name = col.value[len(unit):]
            params[name] = {'description' : name, 'unit': unit} 
        return params

# bit masks
m10 = 0b1111111111
m12 = 0b111111111111
m16 = 0b1111111111111111

# converters
def conv125(x):
    ''' Conversion for EC-TM Moisture/Temp
        VWC in lowest 12 bits (0-11)
        Temp in highest 10 bits (22-31)
     '''
    if np.isnan(x):
        return [np.nan, np.nan]
    raw = np.int32(x)
    R0 = raw & m12
    vwc = 1.09e-3 * R0 - 0.629
    RT = (raw >> 22) & m10
    temp = (RT - 400) / 10.0
    return [vwc, temp]

def conv252(x):
    ''' Conversion for EC-5 Soil Moisture '''
    if np.isnan(x):
        return [np.nan]
    raw = np.int32(x)

    if raw < 290 or raw > 1425:
        return [np.nan]
    return [8.50e-4 * raw - 0.481]

def conv121(x):
    ''' Conversion for MPS-2 Water Potential/Temp
        Water potential in lowest 16 bits (0-15)
        Temp in middle 10 bits (16-25)
     '''
    if np.isnan(x):
        return [np.nan, np.nan]
    raw = np.int32(x)
    Rw = raw & m16
    psi = 10**(0.0001*Rw)/-10.20408
    RT = (raw >> 16) & m10
    if RT <= 900:
        temp = (RT-400) / 10.0
    else:
        temp = ((900 + 5 * (RT-900)) - 400) / 10.0
    return [psi, temp]

def conv119(x):
    ''' conversion for GS3 Moisture/Temp/EC
    Apparent dielectric permittivity (eps) in lowest 12 bits
    Temperature in highest 10 bits
    EC in middle 10 bits 
    '''
    if np.isnan(x):
        return [np.nan,np.nan,np.nan]
    raw = np.int32(x)
    Re = raw & m12
    Ea = Re / 50.0
    vwc = 5.89e-6 * Ea**3 - 7.62e-4 * Ea**2 + 3.67e-2 * Ea -7.53e-2
    
    RT = (raw >> 22) & m10
    if RT <= 900:
        temp = (RT-400) / 10.0
    else:
        temp = ((900 + 5 * (RT-900)) - 400) / 10.0

    Rec = (raw >> 12) & m10
    EC = 10**(Rec/215.0)/1000
    return [vwc, temp, EC]

def conv116(x):
    '''
    conversion for CTD Depth/Temp/EC
    Water level in bits 0-11
    Temperature in bits 22-31
    EC in bits 12-21
    '''
    if np.isnan(x):
        return [np.nan,np.nan,np.nan]
    raw = np.int32(x)
    level = raw & m12
    RT = (raw >> 22) & m10
    if RT <= 900:
        temp = (RT-400) / 10.0
    else:
        temp = ((900 + 5 * (RT-900)) - 400) / 10.0
    Rec = (raw >> 12) & m10
    EC = 10**(Rec/190.0)/1000
    return [level, temp, EC]

def conv187(x):
    ''' conversion for ECRN-100 Precipitation '''
    if np.isnan(x):
        return [np.nan]
    pulses = np.int32(x)
    p = pulses * 0.2 # every pulse = 0.2 mm
    return [p]

def post187(a):
    ''' postprocessor for ECRN-100: calculate precipitation per interval from cumulative values ''' 
    b = []
    b.append([None,])
    for i,x in enumerate(a):
        if(i>0):
            b.append([x[0] - a[i-1][0],])
    return b

def conv189(x):
    ''' conversion for ECRN-50 Precipitation '''
    if np.isnan(x):
        return [np.nan]
    pulses = np.int32(x)
    p = pulses * 1.0 # every pulse = 1 mm
    return [p]

def post189(a):
    ''' postprocessor for ECRN-50: calculate precipitation per interval from cumulative values ''' 
    b = []
    b.append([None,])
    for i,x in enumerate(a):
        if(i>0):
            b.append([x[0] - a[i-1][0],])
    return b
        
SENSORDATA = {
    252: {'converter': conv252,
          'parameters':[{'name': 'VWC', 'description': 'Volumetric water content', 'unit': 'm3/m3'},
                        ]
          },
    121: {'converter': conv121,
          'parameters':[{'name': 'Potential', 'description': 'Water Potential', 'unit': 'kPa'},
                        {'name': 'Temp', 'description': 'Temperature', 'unit': 'oC'}
                        ]
          },
    119: {'converter': conv119,
          'parameters':[{'name': 'VWC', 'description': 'Volumetric water content', 'unit': 'm3/m3'},
                        {'name': 'Temp', 'description': 'Temperature', 'unit': 'oC'},
                        {'name': 'EC', 'description': 'Bulk Electrical Conductivity', 'unit': 'dS/cm'}
                        ]
          },
    116: {'converter': conv116,
          'parameters':[{'name': 'Level', 'description': 'Water level', 'unit': 'mm'},
                        {'name': 'Temp', 'description': 'Temperature', 'unit': 'oC'},
                        {'name': 'EC', 'description': 'Electrical Conductivity', 'unit': 'dS/cm'}
                        ]
          },
    187: { 'converter': conv187,
          'postprocessor': post187,
          'parameters': [{'name': 'Precipitation', 'description': 'Precipitation', 'unit': 'mm'},
                         ]
          },
    189: { 'converter': conv189,
          'postprocessor': post189,
          'parameters': [{'name': 'Precipitation', 'description': 'Precipitation', 'unit': 'mm'},
                         ]
          }
}

# seconds between 1/1/2000 and 1/1/1970
DECATIME_OFFSET = 946684800.0
tz = pytz.timezone(settings.TIME_ZONE)

def decatime(dt):
    try:
        timestamp = float(dt)+DECATIME_OFFSET
        return datetime.datetime.fromtimestamp(timestamp,tz)
    except:
        return None

def date_parser(dt):
    ''' date parser for pandas read_csv '''
    return np.array([decatime(t) for t in dt])

class Dataservice(Generator):
    ''' Decagon Datasevice API '''
        
    def download(self, **kwargs):
        ''' Download dxd file from Decagon dataserver '''
        if not 'deviceid' in kwargs:
            raise DecagonException('Device id ontbreekt')
        if not 'devicepass' in kwargs:
            raise DecagonException('Device password ontbreekt')
        if not 'url' in kwargs:
            raise DecagonException('Url ontbreekt')
        if not 'username' in kwargs:
            raise DecagonException('Username ontbreekt')
        if not 'password' in kwargs:
            raise DecagonException('Password ontbreekt')
        if 'mrid' in kwargs:
            startkey = 'mrid'
            startvalue = int(kwargs['mrid'])
        else:
            startkey = 'time'
            if 'start' in kwargs:
                startvalue = kwargs['start']
            else:
                # 24 hours ago
                startvalue = datetime.datetime.utcnow()-datetime.timedelta(hours=24)
            # convert start to unix utc timestamp
            startvalue = int(time.mktime(startvalue.timetuple()))
        url = kwargs['url'] 

        # TODO: VERWIJDEREN
        #startkey = 'mrid'
        #startvalue = 0
        
        http_header = {'User-Agent': kwargs.get('useragent', 'AcaciaData/1.0')}
        params = {'email': kwargs['username'],
                  'userpass': kwargs['password'],
                  'report': kwargs.get('report',1),
                  'deviceid': kwargs['deviceid'],
                  'devicepass': kwargs['devicepass'],
                  startkey: startvalue
                  }
        data = urllib.urlencode(params)
        http_header['Content-Length'] = len(data)
        request = urllib2.Request(url,data,http_header)
        response = urllib2.urlopen(request)
        if response is None:
            return None
        _,params = cgi.parse_header(response.headers.get('Content-Disposition',''))
        # need unique filename for incremental downloads if we want to keep all downloaded parts
        filename = '%s_%s.dxd' % (kwargs['deviceid'], datetime.datetime.utcnow().strftime('%y%m%d%H%M'))
        #filename = '%s.dxd' % (kwargs['deviceid'])
        filename = kwargs.get('filename', params.get('filename', filename))
        return {filename: response.read()}

    def port2params(self,port):
        ''' determine parameter names from port description
            parameter name is something like Temp P1 (GS3)
            meaning: Temperature from port 1, logger GS3 
        '''
        value = int(port['value'])
        if value == 255:
            return [] # not connected
        if not value in SENSORDATA:
            raise DecagonException('Sensor wordt niet ondersteund: %s' % port['sensor'])
        data = SENSORDATA[value]
        sensor = port['sensor'].split()[0] # short sensor name
        portno = port['number'] # port number
        postfix = ' P%s (%s)' % (portno, sensor)
        params = [] # use array instead of dict to keep params in correct order
        for p in data['parameters']:
            name = p['name'] + postfix
            params.append({'name': name, 'description': p['description'], 'unit': p['unit']})
        return params
    
    def _get_parameters(self, tree):
        params = [] # use array instead of dict to keep params in correct order
        device = tree.find('Device')
        for port in device.findall('Configuration/Measurement/Ports/Port'):
            p = self.port2params(port.attrib)
            if p != []:
                params.extend(p)
        return params

    def get_parameters(self, f):
        tree = ET.ElementTree()
        tree.parse(f)
        params = self._get_parameters(tree)
        result = {}
        # convert array of params to dict with key param.name
        for p in params:
            result[p['name']] = {'description': p['description'], 'unit': p['unit']}
        return result
    
    def get_data(self, f, **kwargs):
        tree = ET.ElementTree()
        tree.parse(f)
        device = tree.find('Device')
        data = device.find('Data')
        io = StringIO.StringIO(data.text)

        # read raw port values into dataframe, converting decatime to python datetime 
        # TODO: skip records with date/time = None 
        df = pd.read_csv(io, header=None, index_col=[0], skiprows = 1, skipinitialspace=True, parse_dates = True, date_parser = date_parser)

        ports = device.findall('Configuration/Measurement/Ports/Port')
        nports = len(ports)
        ncols = len(df.columns)
        if nports != ncols:
            raise DecagonException('Aantal datakolommen (%d) is niet gelijk aan aantal poorten (%d)' % (ncols, nports))
        df.index.name = 'Datum/Tijd'
        df.columns = ['%s%d' % ('port', i+1) for i in range(nports)]
        for elem in ports:
            port = elem.attrib
            value = int(port['value'])
            if value == 255:
                continue
            params = self.port2params(port)
            data = SENSORDATA[value]
            convert = data['converter']
            label = 'port%s' % port['number']
            raw = df[label]
            values = [convert(x) for x in raw]
            process = data.get('postprocessor',None)
            if process is not None:
                values = process(values)
            for i,p in enumerate(params):
                data = [x[i] for x in values]
                df[p['name']] = pd.Series(data, index = df.index)
                df.dropna(how='all',inplace=True)
        return df
    
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET


def parse_test(filename):
    tree = ET.ElementTree(file=filename)
    root = tree.getroot()
    print root.tag, root.attrib
    for device in tree.findall('Device'):
        print device.tag, device.attrib
        for port in device.findall('Configuration/Measurement/Ports/Port'):
            print port.tag, port.attrib
    data = device.find('Data')
    print data.tag, data.attrib
    io = StringIO.StringIO(data.text)        
    df = pd.read_csv(io, header=None, index_col=[0], skiprows = 1, skipinitialspace=True, parse_dates = True, date_parser = date_parser)
    return df
    
def download_test():
    url = 'http://api.ech2odata.com/spaarwater/dxd.cgi' 
    http_header = {'User-Agent': 'Decagon_curl_example-01'}
    params = {'email':      'no-email@acaciawater.com',
              'userpass':   'zuEti*rCd0',
              'report':     1,
              'deviceid':   '5G0E2930',
              'devicepass': 'juat-apty',
              'mrid':       2000
              }
    data = urllib.urlencode(params)
    http_header['Content-Length'] = len(data)
    request = urllib2.Request(url,data,http_header)
    response = urllib2.urlopen(request)
    return response.read()
    
if __name__ == '__main__':
    api = Dataservice()

    params = {
              'url':        'http://api.ech2odata.com/spaarwater/dxd.cgi',
              'username':   'no-email@acaciawater.com',
              'password':   'zuEti*rCd0',
              'deviceid':   '5G0E2933',
              'devicepass': 'ejcee-lilf',
              #'deviceid':   '5G0E2930',
              #'devicepass': 'juat-apty',
              }
#     result = api.download(**params)
#     for filename, content in result.iteritems():
#         with open(filename, 'w') as f:
#             f.write(content)
    
    filename = '/home/theo/git/acacia-data/acacia/acacia/data/generators/5G0E2933.dxd'
    
    with open(filename) as f:
        params = api.get_parameters(f)
        for p in params.items():
            print p

    with open(filename) as f:
        data = api.get_data(f)
        print data
    
        
#     result = parse_test()
#     print result
    

#    result = download_test()
#    print result
    
#     
#     with open('/home/theo/breez/535NorI-10Mar2014-1443.xls') as f:
#         dt = DataTrac()
#         params = dt.get_parameters(f)
#         data = dt.get_data(f)
#         print data
#     