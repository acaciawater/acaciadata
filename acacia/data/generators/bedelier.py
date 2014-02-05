import pandas as pd
import logging
import urllib2
logger = logging.getLogger(__name__)

from generator import Generator

class OWB(Generator):
        
    def __init__(self, *args, **kwargs):
        super(OWB, self).__init__(args,kwargs)
        self.args = {'url': 'ftp://bedelier:reiledeb@grondwatertoolbox.nl'}

    def get_header(self, f):
        # voor Borgsweer (met 3 onttrekkings putten)
        cols = ['Algemeen_datum_', 'Algemeen_tijd_', 'Algemeen_BronIn m3_', 'systeem1__rust', 'systeem1__infiltreren', 'systeem1__ontrekken', 
                'systeem1__EC bronuit', 'systeem1__Bronuit m3', 'systeem1__bronuit minzand m3', 'systeem1_Bron1_Speed %', 'systeem1_Bron1_EC', 
                'systeem1_Bron1_Bronuit m3', 'systeem1_Bron1_Bronintot m3', 'systeem1_Bron2_Speed %', 'systeem1_Bron2_EC', 'systeem1_Bron2_Bronuit m3', 
                'systeem1_Bron2_Bronintot m3', 'systeem1_Bron3_Speed %', 'systeem1_Bron3_EC', 'systeem1_Bron3_Bronuit m3', 'systeem1_Bron3_Bronintot m3', 
                'systeem2__rust', 'systeem2__infiltreren', 'systeem2__ontrekken', 'systeem2__EC bronuit', 'systeem2__Bronuit m3', 'systeem2__bronuit minzand m3', 
                'systeem2_Bron1_Speed %', 'systeem2_Bron1_EC', 'systeem2_Bron1_Bronuit m3', 'systeem2_Bron1_Bronintot m3', 'systeem2_Bron2_Speed %', 
                'systeem2_Bron2_EC', 'systeem2_Bron2_Bronuit m3', 'systeem2_Bron2_Bronintot m3', 'systeem2_Bron3_Speed %', 'systeem2_Bron3_EC', 
                'systeem2_Bron3_Bronuit m3', 'systeem2_Bron3_Bronintot m3']
        sections = {}
        sections['COLUMNS'] = cols
        return sections
    
    def get_file(self, path):
        response = urllib2.urlopen(self.url + '/' + path)
        return response
        
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        data = pd.read_csv(f, header=None, sep = ';', index_col = 0, parse_dates = {'datum': [0,1]}, dayfirst = True)
        if data is not None:
            names = header['COLUMNS'][2:]
            names.append('Laatste kolom')
            data.columns = names
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][2:]
        params = [{'name': name, 'description' : name, 'unit': '-'} for name in names]  
        return params
        
if __name__ == '__main__':
    with open('/home/theo/git/acacia-data/acacia/media/datafiles/Borgsweer_LogFile.csv') as f:
        o = OWB()
        data = o.get_data(f)
        print data
