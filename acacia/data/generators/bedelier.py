import logging
logger = logging.getLogger(__name__)

from generator import Generator

COL_LOOKUP = {'L': 'Watermeter Bron1 Uit 1 [0.1 m3]', 'M': 'Watermeter Bron1 Uit 2 [0.1 m3]', 'N': 'Watermeter Bron1 Uit 3 [0.1 m3]', 'O': 'Watermeter Bron1 Uit 4 [0.1 m3]',
               'P': 'Watermeter Bron2 Uit 1 [0.1 m3]', 'Q': 'Watermeter Bron2 Uit 2 [0.1 m3]', 'R': 'Watermeter Bron2 Uit 3 [0.1 m3]', 'S': 'Watermeter Bron2 Uit 4 [0.1 m3]'}

class OWB(Generator):
        
    def get_header(self, f):
        cols = [col.strip() for col in f.readline().split(';')]
        for i,col in enumerate(cols):
            if col == '':
                col = str(unichr(ord('A')+i))
                if col in COL_LOOKUP:
                    cols[i] = COL_LOOKUP[col]
        sections = {}
        sections['COLUMNS'] = cols
        self.skiprows = 1
        return sections
            
    def get_data(self, f, **kwargs):
        header = self.get_header(f)
        data = self.read_csv(f, header=None, sep = ';', index_col = 0, parse_dates = {'datum': [0,1]}, dayfirst = True)
        if data is not None:
            names = header['COLUMNS'][2:]
            #names.append('Laatste kolom')
            data.columns = names
        return data

    def get_parameters(self, fil):
        header = self.get_header(fil)
        names = header['COLUMNS'][2:]
        params = {}
        for name in names:
            params[name] = {'description' : name, 'unit': '-'} 
        return params
    
if __name__ == '__main__':
    with open('/home/theo/acacia/data/Breezand/LogFile140221.csv') as f:
        o = OWB()
        data = o.get_data(f)
        print data
