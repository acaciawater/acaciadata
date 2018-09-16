from django.db import connection
from acacia.data.models import DataPoint
import dateutil
import datetime

#group by 12 hours
#select concat(day,' ',lpad(h,2,0),':00:00') as date, value from (
#select date(`date`) day, hour(`date`) as h, avg(value) value from delft.data_datapoint where series_id=1433 group by day, h div 12) as t;

#group by 3 days:
#select date(date) as day, value from delft.data_datapoint where series_id=1433 group by day div 3

# group by month:
#select concat(y,'-',lpad(m,2,0),'-01') as date, value from 
#(select year(p.date) as y, month(p.date) as m, avg(p.value) as value from delft.data_datapoint p where series_id = 1433 group by y, m) as t2;

# group by year:
#select year(date) as year, value from delft.data_datapoint where series_id=1433 group by year

class Sampler(object):
    
    _periods = {
        'h': 'HOUR',
        'd': 'DAY',
        'w': 'WEEK',
        'm': 'MONTH',
        'y': 'YEAR'
        }

    def period_from_key(self,key):
        return self._periods.get(key)
#         for k,v in self._periods.items():
#             if key.startswith(k):
#                 return v
#         return None

    def parse_interval(self, interval):
        ''' parse interval for queries '''
        ''' interval consists of (optional) count and period and is something like 7d, 1w, 6h etc '''
        import re
        pattern = '^(?P<count>\d?)(?P<period>\w+)$'
        match = re.match(pattern, interval)
        if not match:
            raise ValueError('invalid interval')
        count = int(match.group('count') or '1')
        period = self.period_from_key(match.group('period').lower())
        if period is None:
            raise ValueError('invalid period')
        return (int(count), period)

    def sample(self, series, start, stop, interval):
        raise NotImplemented
    
class MySQL(Sampler):

    def sample(self, series, start, stop, interval):
        count, period = self.parse_interval(interval)
        templates = {'HOUR': "select concat(day,' ',lpad(h,2,0),':00:00') as date, value from ( \
                     select date(`date`) day, hour(`date`) as h, avg(value) value from data_datapoint p \
                     {where} \
                     group by day, h div {count}) as t;",
                     
                     'DAY': "select concat(day,' 00:00:00') as date, value from (\
                     select date(date) day, avg(value) value from data_datapoint p \
                     {where} \
                     group by day div {count}) as t;",
                     
                     'MONTH': "", #TODO
                     'YEAR': "" #TODO
        }
        where = 'where p.series_id={id}'.format(id=series.id)
        if start:
            where += " and p.date > '{start}'".format(start=start)
        if stop:
            where += " and p.date < '{stop}'".format(stop=stop) 
        template = templates[period]
        query = template.format(where=where,count=count)
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            while True:
                row = cursor.fetchone()
                if row:
                    row = dict(zip(columns,row))
                    date = dateutil.parser.parse(row['date'])
                    yield DataPoint(series_id=series.id,date=date,value=row['value'])
                else:
                    break
        
class Postgres(Sampler):
    def sample(self, series, interval):
        pass
    