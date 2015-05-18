'''
Created on Jan 28, 2015

@author: theo
'''
import logging
from logging import handlers

from acacia.data.models import Datasource
  
class AutoFlushLoggingAdapter(logging.LoggerAdapter):
 
    def flush(self):
        ''' call flush() on all handlers '''
        if self.logger is not None:
            for h in self.logger.handlers:
                if hasattr(h,'flush'):
                    h.flush()
     
    def __enter__(self):
        return self
 
    def __exit__(self, _type, _value, _traceback):
        ''' called when with block terminates '''
        self.flush()
      
class DatasourceAdapter(AutoFlushLoggingAdapter):
     
    stack = []
    datasource = None
    
    def __init__(self,logger,datasource=None):
        self.push(datasource)
        return super(DatasourceAdapter,self).__init__(logger, datasource)
     
    def process(self, msg, kwargs):
        kwargs['extra'] = {'datasource': self.datasource}
        return (msg, kwargs)
 
    def push(self,ds):
        self.stack.append(ds)
        self.datasource = ds
        return self.datasource
     
    def pop(self):
        self.datasource = self.stack.pop()
        return self.datasource
     
class BulkEmailHandler(handlers.BufferingHandler):
    
    def __init__(self, fromaddr, subject, capacity):
        super(BulkEmailHandler,self).__init__(capacity)
        self.fromaddr = fromaddr
        self.subject = subject
  
    def group_records_by_email(self, records):
        group = {}
        for record in records:
            if hasattr(record,'datasource'):
                if isinstance(record.datasource, Datasource):
                    for n in record.datasource.notification_set.filter(active=True):
                        nlvl = logging.getLevelName(n.level)
                        rlvl = record.levelno
                        if nlvl <= rlvl: 
                            if n in group:
                                group[n].append(record)
                            else:
                                group[n] = [record]
        return group
             
    def flush(self):
        if len(self.buffer) > 0:
            try:
                from django.core.mail import send_mail
                grp = self.group_records_by_email(self.buffer)
                for notify, records in grp.items():
                    msg = '\n'.join([self.format(r) for r in records])
                    send_mail(notify.subject, msg, self.fromaddr, [notify.email])
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                raise
                #self.handleError(None)
        self.buffer = [] 
                
# h=BulkEmailHandler(fromaddr='webmaster@acaciadata.com', subject='Houston, we have a problem', capacity=10)
# f=logging.Formatter('%(levelname)s %(asctime)s %(datasource)s: %(message)s')
# h.setFormatter(f)
# l=logging.getLogger('acacia.data').addHandler(h)
