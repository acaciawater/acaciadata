'''
Created on Jan 26, 2014

@author: theo
'''
import pandas as pd
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

    def get_data(self,f):
        sections = self.get_header(f)
        channels = ['DATE']
        num = int(sections['Logger settings'].get('Number of channels'))
        for i in range(1,num+1):
            name = sections['Channel %d' % i].get('Identification')
            channels.append(name)
        num = int(f.readline())
        widths = [22,13,12,12]
        df = pd.read_fwf(f, header=None, index_col='DATE', widths=widths, names=channels, parse_dates = True )
        return [sections, df]

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = []
        num = 1
        channel = 'Channel 1'
        while channel in header:
            names.append(header[channel]['Identification'])
            num = num + 1
            channel = 'Channel %d' % num
        params = [{'name': name, 'description' : name, 'unit': 'unknown'} for name in names]  
        return params
