'''
Created on Jan 28, 2015

@author: theo
'''
import logging
from logging import handlers

class AutoFlushLoggingAdapter(logging.LoggerAdapter):
    ''' loggingadapter that automatically calls flush when destroyed. Can be used in 'with' block '''  
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
    ''' Lopgging adapter that adds datasource to log records '''
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

from threading import Timer
class TimedBufferingHandler(handlers.BufferingHandler):
    ''' Buffering handler that calls flush after interval seconds. Used to collect logrecords and send emails '''
    def __init__(self, capacity, interval):
        super(TimedBufferingHandler,self).__init__(capacity)
        self.interval = interval
        self.timer = Timer(self.interval, self.flush)

    def emit(self, record):
        super(TimedBufferingHandler,self).emit(record)
        self.timer.cancel()
        self.timer = Timer(self.interval, self.flush)
        self.timer.start()

from acacia.data.models import Datasource

class BufferingEmailHandler(TimedBufferingHandler):
    
    def __init__(self, fromaddr, subject, capacity, interval):
        super(BufferingEmailHandler,self).__init__(capacity,interval)
        self.fromaddr = fromaddr
        self.subject = subject
  
    def group_records_by_email(self, records):
        group = {}
        for record in records:
            if hasattr(record,'datasource'):
                if isinstance(record.datasource, Datasource):
                    for n in record.datasource.notification_set.filter(active=True):
                        email = n.email
                        nlvl = logging.getLevelName(n.level)
                        rlvl = record.levelno
                        if nlvl <= rlvl: 
                            if email in group:
                                group[email].append(record)
                            else:
                                group[email] = [record]
        return group

    def group_records(self, records):
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
    
    def format_message(self, records):
        ''' formats log records as html '''
        from django.template.loader import render_to_string
        # group records by datasource
        ds = {}
        for r in records:
            if not r.datasource in ds:
                ds[r.datasource] = [r]
            else:
                ds[r.datasource].append(r)
        return render_to_string('data/notify_email.html', {'data': ds})

    def send_html_mail(self, subject, message, from_email, recipient_list,
                  fail_silently=False, auth_user=None, auth_password=None,
                  connection=None):
        ''' send email as html '''
        from django.core.mail import get_connection, EmailMessage
        connection = connection or get_connection(username=auth_user,
                                        password=auth_password,
                                        fail_silently=fail_silently)
        m = EmailMessage(subject, message, from_email, recipient_list, connection=connection)
        m.content_subtype = "html"
        return m.send()
    
    def flush(self):
        if len(self.buffer) == 0:
            return

        try:
            grp = self.group_records_by_email(self.buffer)
            for email, records in grp.items():
                msg = self.format_message(records)
                ds = set([r.datasource for r in records])
                if len(ds) == 1:
                    subject = 'Update of %s' % ds.pop()
                else:
                    # meerdere datasources
                    pr = set([d.project() for d in ds])
                    if len(pr) == 1:
                        subject = '%s updates' % pr.pop()
                    else:
                        subject = 'acaciadata.com update'
                self.send_html_mail(subject, msg, self.fromaddr, [email])
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            raise
            #self.handleError(None)
        self.buffer = [] 
                
# h=BufferingEmailHandler(fromaddr='webmaster@acaciadata.com', subject='Houston, we have a problem', capacity=10)
# f=logging.Formatter('%(levelname)s %(asctime)s %(datasource)s: %(message)s')
# h.setFormatter(f)
# l=logging.getLogger('acacia.data').addHandler(h)
