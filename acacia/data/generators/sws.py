'''
Created on Jan 26, 2014

@author: theo
'''
import logging
from generator import Generator
logger = logging.getLogger(__name__)

class MonFileException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Diver(Generator):

    def get_header(self,f):
        line = f.readline()
        if not line.startswith('Data file for DataLogger.'):
            raise MonFileException('%s is not recognized as mon file' % f.name )
        line = f.readline()
        if not line.startswith('====='):
            raise MonFileException('%s is not recognized as mon file' % f.name )
        header = {}
        while True:
            line = f.readline()
            if 'BEGINNING OF DATA' in line:
                break
            colon = line.find(':')
            if colon < 0:
                raise MonFileException('colon expected parsing line \'%s\'' % line )
            key = line[0:colon].strip()
            if key == '':
                continue
            value = line[colon+1:].strip()
            header[key] = value
        sections = {}
        sections['HEADER'] = header
        section = {}
        sections['DEFAULT'] = section
        while True:
            line = f.readline().strip()
            if line == '':
                continue
            if line == '[Data]':
                break
            if line.startswith('['):
                name = line.strip('[]').strip()
                section = {}
                sections[name] = section
            else:
                delim = line.find('=')
                if delim < 0:
                    continue
                key = line[0:delim].strip()
                value = line[delim+1:].strip()
                section[key] = value
        return sections

    def get_data(self,f,**kwargs):
        sections = self.get_header(f)
        names = ['DATE','TIME']
        num = int(sections['Logger settings'].get('Number of channels'))
        for i in range(1,num+1):
            name = sections['Channel %d' % i].get('Identification')
            names.append(name)
        num=int(f.readline())
        data = self.read_csv(f, header=0, index_col=0, names = names, delim_whitespace=True, parse_dates = {'date': [0,1]}, nrows=num-1)
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        params = []
        num = int(header['Logger settings'].get('Number of channels'))
        for i in range(1,num+1):
            channel = 'Channel %d' % i
            name = header[channel].get('Identification',None)
            if name is not None:
                params[name] = {'description': channel, 'unit': 'unknown'}  
        return params
