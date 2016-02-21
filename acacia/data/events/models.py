from django.db import models
from ..models import Series
from django.contrib.auth.models import User
import pandas as pd

FREQ = (('T', 'minuut'),
        ('15T', 'kwartier'),
        ('H', 'uur'),
        ('D', 'dag'),
        ('W', 'week'),
        ('M', 'maand'),
        ('A', 'jaar'),
        )
HOW = (('mean', 'gemiddelde'),
        ('median', 'mediaan'),
        ('max', 'maximum'),
        ('min', 'minimum'),
        ('sum', 'som'),
        )
HILO = (('>', 'boven'), ('<', 'onder'))

class Trigger(models.Model):
    name = models.CharField(max_length=100)
    series = models.ForeignKey(Series)
    hilo = models.CharField(max_length=1,choices=HILO)
    level = models.FloatField()
    freq = models.CharField(max_length=8,choices=FREQ,blank=True, null=True, verbose_name='frequentie')
    how = models.CharField(max_length=16,choices=HOW,blank=True, null=True, verbose_name='methode')
    window = models.IntegerField(default=1)
    count = models.IntegerField(default=1)
            
    def __unicode__(self):
        return self.name
    
    def source(self):
        return unicode(self.series)
    
    def select(self,**kwargs):        
        s = self.series.to_pandas(**kwargs)
        window = max(self.window,self.count)
        min_periods = min(window,self.count)
        if self.how:
            method = 'rolling_'+ self.how
            method=getattr(pd,method)
            s=method(arg=s, window=window, min_periods=min_periods, freq=self.freq, center=False, how=self.how)
        if self.hilo == '>':
            s = s[s>self.level]
        else:
            s = s[s<self.level]
        return s

ACTIONS = ((0, 'ignore'),
           (1, 'email'),
           (2, 'sms'),
           )

class Target(models.Model):
    user = models.ForeignKey(User)
    cellphone = models.CharField(max_length=12)
    email = models.EmailField()
    
    def __unicode__(self):
        return self.user.username
    
class Event(models.Model):
    trigger = models.ForeignKey(Trigger)
    target = models.ForeignKey(Target)
    action = models.IntegerField(default = 0, choices=ACTIONS)
    
    def __unicode__(self):
        return self.trigger.name

    def format_message(self, date, value, html=False):
        if html:
            return '<p>{evt} was triggered on {date}<br/>Details: {ser} = {value}</p>'.format(evt=str(self.trigger), ser=str(self.trigger.series),date=date,value=value)
        else:
            return '{evt} was triggered on {date}\r\nDetails: {ser} = {value}'.format(evt=str(self.trigger), ser=str(self.trigger.series),date=date,value=value)

ONOFF = ((0, 'off'),(1,'on'))

class History(models.Model):
    
    class Meta:
        verbose_name = 'Geschiedenis'        
        verbose_name_plural = 'Geschiedenis'
        
    event = models.ForeignKey(Event)
    date = models.DateTimeField(auto_now = True)
    state = models.IntegerField(default=1, choices=ONOFF)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    
    def user(self):
        return self.event.target.user
    
    def format_html(self):
        return '<h4>{evt}</h4>{msg}'.format(evt=self.event.trigger.name,msg=self.message)
        
    def __unicode__(self):
        return self.event.trigger.name

    message.allow_tags = True