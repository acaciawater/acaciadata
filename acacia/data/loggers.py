'''
Created on Jan 28, 2015

@author: theo
'''
import logging
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
    
    def __init__(self,logger,datasource=None):
        self.datasource = datasource
        return super(DatasourceAdapter,self).__init__(logger, datasource)
    
    def process(self, msg, kwargs):
        kwargs['extra'] = {'datasource': self.datasource}
        return (msg, kwargs)

class BulkEmailHandler(logging.handlers.BufferingHandler):
    
    def __init__(self, fromaddr, subject, capacity):
        super(BulkEmailHandler,self).__init__(capacity)
        self.fromaddr = fromaddr
        self.subject = subject

    def group_records_by_user(self, records):
        group = {}
        for record in records:
            if isinstance(record.datasource, Datasource):
                for user in [n.user for n in record.datasource.notification_set.all()]:
                    if user in group:
                        group[user].append(record)
                    else:
                        group[user] = [record]
        return group
            
    def flush(self):
        if len(self.buffer) > 0:
            try:
                from django.core.mail import send_mail
                grp = self.group_records_by_user(self.buffer)
                for user, records in grp.items():
                    msg = '\n'.join([self.format(r) for r in records])
                    send_mail(self.subject, msg, self.fromaddr, [user.email])
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                raise
                #self.handleError(None)
        self.buffer = [] 