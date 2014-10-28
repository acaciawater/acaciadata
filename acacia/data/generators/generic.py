import logging
logger = logging.getLogger(__name__)

from generator import Generator

class Generic(Generator):
    ''' Generic csv file without header, comma separated, uses standard date/time formatting in first column '''

    def __init__(self, *args, **kwargs):        
        super(Generic,self).__init__(*args, **kwargs)
        self.header = kwargs.get('header', None)

    def set_labels(self,data):
        if self.header is None:
            # provide default column labels
            cols = data.shape[1]
            data.columns = ['Channel%d'%(i+1) for i in range(cols)]
            data.index.name = 'Date'
        return data.columns
    
    def get_data(self, f, **kwargs):
        data = self.read_csv(f, parse_dates = True, index_col = 0, header = self.header)
        self.set_labels(data)
        data.dropna(inplace=True)
        return data

    def get_parameters(self, f):
        data = self.read_csv(f, parse_dates = True, nrows=1, index_col = 0, header = self.header)
        self.set_labels(data)
        params = {}
        colno = 1
        for col in data.columns:
            params[col] = {'description' : 'Column %d' % colno, 'unit': '-'}
            colno += 1 
        return params

class GenericCSV(Generic):
    def __init__(self, *args, **kwargs):
        kwargs['header'] = 0        
        super(GenericCSV,self).__init__(*args, **kwargs)
        
from StringIO import StringIO
if __name__ == '__main__':
    g = Generic()
    data = '2014-9-12 12:00,2,3,4\n2014-9-13 13:00,6,7,8\n'
    f = StringIO(data)
    p = g.get_parameters(f)
    f.seek(0)
    data = g.get_data(f)
    print data
