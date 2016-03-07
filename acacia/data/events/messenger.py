'''
Created on Feb 20, 2016

@author: theo
'''

from django.conf import settings
from .models import ACTION_EMAIL, ACTION_SMS

class Messenger():
    ''' buffers triggered events and automatically sends messages to users through email or sms'''

    def __init__(self, event):
        assert event, 'Event cannot be None'
        self.event = event
        self.unsent = list(event.history_set.filter(sent=False))
        
    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        if self.unsent:
            self.send_messages()
 
    def send_sms(self, originator, body, recipients):
        import messagebird
        client = messagebird.Client(settings.MESSAGEBIRD_APIKEY)
        params = {}
        msg = client.message_create(originator, recipients, body, params)
        return msg
        
    def send_email(self,subject, message, from_email, recipient_list,
                  fail_silently=False, auth_user=None, auth_password=None,
                  connection=None,html=False):
        from django.core.mail import get_connection, EmailMessage
        connection = connection or get_connection(username=auth_user,
                                        password=auth_password,
                                        fail_silently=fail_silently)
        m = EmailMessage(subject, message, from_email, recipient_list, connection=connection)
        if html:
            m.content_subtype = 'html'
        return m.send()

    def send_messages(self):
        message = self.event.message
        try:
            if self.event.action == ACTION_EMAIL:
                if not message:
                    message ='\r\n'.join([h.format_html() for h in self.unsent])
                success = self.send_email('Acaciadata Alarm', message, 'alarm@acaciadata.com', [self.event.target.email], html=True)
            elif self.event.action == ACTION_SMS:
                if not message:
                    message = 'Event {evt} was triggered {count} times'.format(evt=str(self.event.trigger), count=len(self.unsent))
                success = self.send_sms('Acaciadata', message, self.event.target.cellphone)
        except Exception as e:
            logger.exception('Failed to send alarm message to {dest}: {ex}'.format(dest=unicode(self.event.target),ex=e))
            success = False
        if success:
            for h in self.unsent:
                h.sent=True
                h.save()
            
    def add(self, message):
        self.unsent.append(self.event.history_set.create(message=message, sent=False))

import logging
logger = logging.getLogger(__name__)

def process_events(series):

    # group events by trigger
    from itertools import groupby
    key = lambda e:e.trigger
    events = sorted(series.event_set.all(),key=key)
    eventgroups = groupby(events,key=key)
 
    total = 0
    for trigger,group in eventgroups:
        # get last message sent for this trigger
        start = None
        events = list(group)
        # remember last message sent
        sent = {}
        for e in events:
            history = e.history_set.filter(sent=True).order_by('-date')
            if history:
                last = history[0].date
                sent[e] = last
                start = min(start, last) if start else last
                
        # select offending data points after last message sent
        data = trigger.select(series,start=start)
        num = data.count()
        if num > 0:
            total += num
            # there are some alarms to be sent
            for e in events:
                last = sent.get(e,None)
                with Messenger(e) as m:
                    # add message for every event
                    for date,value in data.iteritems():
                        if last and date <= last:
                            # dont send message twice
                            continue
                        m.add(e.format_message(date,value,html=True))
                    msg = 'Event {name} was triggered {count} times for {ser} since {date}'.format(name=e.trigger.name, count=num, ser=series,date=start)
        else:
            msg = 'No alarms triggered for trigger {name} since {date}'.format(date=start, name=trigger.name)
        logger.debug(msg)
    if total > 0:
        msg = '{name}: {num} alarms were triggered'.format(name=series.name, num=total)
        logger.info(msg)
    return total

'''
def process_triggers(series):
    # send messages to targets when events are triggered for time series
    total = 0
    for t in series.trigger_set.all():
        # get last message set for this trigger
        start = None

        # remember last message sent
        sent = {}
        
        for e in t.event_set.all():
            history = e.history_set.filter(sent=True).order_by('-date')
            if history:
                last = history[0].date
                sent[e] = last
                start = min(start, last) if start else last
                
        # select offending data points after last message sent
        data = t.select(start=start)
        num = data.count()
        if num > 0:
            total += num
            # there are some alarms to be sent
            for e in t.event_set.all():
                last = sent.get(e,None)
                with Messenger(e) as m:
                    # add message for every event
                    for date,value in data.iteritems():
                        if last and date <= last:
                            # dont send message twice
                            continue
                        m.add(e.format_message(date,value,html=True))
                    msg = 'Event {name} was triggered {count} times for {ser} since {date}'.format(name=e.trigger.name, count=num, ser=series,date=start)
        else:
            msg = 'No alarms triggered for trigger {name} since {date}'.format(date=start, name=t.name)
        logger.debug(msg)
    if total > 0:
        msg = '{name}: {num} alarms were triggered'.format(name=series.name, num=total)
        logger.info(msg)
'''