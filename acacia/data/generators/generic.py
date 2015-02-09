import logging
logger = logging.getLogger(__name__)

import pandas as pd

from generator import Generator

class Generic(Generator):
    ''' Generic csv file without header, comma separated, uses standard date/time formatting in first column '''

    def __init__(self, *args, **kwargs):        
        super(Generic,self).__init__(*args, **kwargs)
        self.header = kwargs.get('header', None)
        self.dayfirst = kwargs.get('dayfirst', False)

    def set_labels(self,data):
        if self.header is None:
            # provide default column labels
            cols = data.shape[1]
            data.columns = ['Channel%d'%(i+1) for i in range(cols)]
            data.index.name = 'Date'
        return data.columns

    def get_data(self, f, **kwargs):
        data = self.read_csv(f, parse_dates = True, index_col = 0, header = self.header, dayfirst = self.dayfirst)
        self.set_labels(data)
        if not isinstance(data.index,pd.DatetimeIndex):
            # for some reason dateutil.parser.parse not always recognizes valid dates?
            data.drop('None', inplace = True)
            data.index = pd.to_datetime(data.index)
        data.dropna(how='all', inplace=True)
        return data

    def get_parameters(self, f):
        data = self.read_csv(f, parse_dates = [0], nrows=1, index_col = 0, header = self.header, dayfirst = self.dayfirst)
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

#if __name__ == '__main__':
#    g = Generic()
#    data = '2014-9-12 12:00,2,3,4\n2014-9-13 13:00,6,7,8\n'
#    f = StringIO(data)
#    p = g.get_parameters(f)
#    f.seek(0)
#    data = g.get_data(f)
#    print data

# if __name__ == '__main__':
#     g = GenericCSV(dayfirst=True)
#     data = 'Datum, een, twee, drie, vier, vijf, zes\n"30-04-2014 12:00", 2749, 109, 4.7, 1882, 149, 2.9\n"7-5-2014 12:00", 1140, 115, 5.9, 806, 122, 6.1\n"14-5-2014 12:00", 3500, 156, 2.7, 991, 188, 4.6\n'
#     f = StringIO(data)
#     p = g.get_parameters(f)
#     f.seek(0)
#     data = g.get_data(f)
#     print data

src = '/home/theo/acaciadata.com/texel/media/proef-zoetwaterberging/proefperceel/referentie-veld/datafiles/koenders-2015-ref/2015REF_33.LOG'
src = '/home/theo/data/koenders/2015FER1_52.LOG'

if __name__ == '__main__':
    g = Generic()
    with open(src,'rb') as f:
        data = g.get_data(f)
    print data.index
    print data
