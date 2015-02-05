'''
Created on Jan 28, 2015

@author: theo
'''
import logging
from acacia.data.models import Datasource
 
class DatasourceAdapter(logging.LoggerAdapter):
    
    def __init__(self,logger,datasource=None):
        self.datasource = datasource
        return super(DatasourceAdapter,self).__init__(logger, datasource)
    
    def process(self, msg, kwargs):
        kwargs['extra'] = {'datasource': self.datasource}
        return (msg, kwargs)

    def flushAll(self):
        for h in self.logger.handlers:
            if hasattr(h,'flush'):
                h.flush()
            
class BulkEmailHandler(logging.handlers.BufferingHandler):
    
    def __init__(self, mailhost, fromaddr, toaddrs, subject, capacity,
                 credentials=None, secure=None):
        super(BulkEmailHandler,self).__init__(capacity)
        if isinstance(mailhost, tuple):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None
        if isinstance(credentials, tuple):
            self.username, self.password = credentials
        else:
            self.username = None
        self.fromaddr = fromaddr
        if isinstance(toaddrs, basestring):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure

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