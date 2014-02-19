'''
Created on Jan 29, 2013

@author: theo
'''
#from ...data.util import find_files
import zipfile,os,fnmatch
import pandas as pd
import logging

from .generator import Generator

logger = logging.getLogger(__name__)

def find_files(pattern, root=os.curdir):
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

class Dino(Generator):

    def skip_section(self,f):
        while True:
            line=f.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                break
        
    def load_header(self,f):
        line = f.readline()
        while line:
            line = line.strip()
            if line:
                return line.split(',')
            line = f.readline()
        return None

    def load_well(self,f):
        keys = self.load_header(f)
        data = []
        line = f.readline()
        while line:
            line = line.strip()
            if line:
                values =line.split(',')
                data = dict(zip(keys,values))
                line = f.readline()
        return data
        
    def load_data(self,f):
        header = self.load_header(f)
        data = []
        line = f.readline()
        while line:
            line = line.strip()
            if line:
                tokens=line.split(',')
                locatie = tokens[0]
                filternummer = tokens[1]
                peildatum = tokens[2]
                stand_mp= tokens[3]
                stand_mv= tokens[4]
                stand_nap= tokens[5]
                data.append((locatie,filternummer,peildatum,stand_mp,stand_mv,stand_nap))
            line = f.readline()
        return data
    
    def load_file(self,f):
        self.skip_section(f)
        self.skip_section(f)
        try:
            well=self.load_well(f)
            well['standen']=self.load_data(f)
            return well
        except:
            return None
    
    def load_folder(self,folder):
        result = []
        for name in find_files('*_1.csv', folder):
            f=open(name,'r')
            data = self.load_file(f)
            if data:
                result.append(data)
        return result

    def load_zip(self,filename):
        result = []
        with zipfile.ZipFile(filename,'r') as z:
            for info in z.infolist():
                if info.filename.endswith('_1.csv'):
                    f=z.open(info.filename,'r')
                    data = self.load_file(f)
                    if data:
                        result.append(data)
        return result

    def __init__(self,**kwargs):
        super(Dino,self).__init__(**kwargs)
    
    def get_header(self,fil):
        self.skip_section(fil)
        self.skip_section(fil)
        self.skip_section(fil)
        return self.load_header(fil)

    def get_data(self,fil,**kwargs):
        hdr = self.get_header(fil)
        hdr.append('') # dino csv format is not correct
        for i in range(0,len(hdr)):
            if hdr[i] == '':
                hdr[i] = 'veld%d' % (i+1)
        data = pd.read_csv(fil, header=0, names = hdr, index_col = [2], dayfirst=True, parse_dates = [2])
        return data

    def get_parameters(self,fil):
        header = self.get_header(fil)
        params = []
        for p in header[3:]: 
            if len(p)>0:
                params.append({'name': p, 'description': p, 'unit': '-'})
        return params
    
if (__name__ == '__main__'):
    dino=Dino()
    dino.load_zip('/media/sf_C_DRIVE/projdirs/spaarwater/borgsweer/4c33a801-7366-4c2d-b61b-39f34e5f8507.zip')
