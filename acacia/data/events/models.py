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
HILO = (('>', 'boven'), ('<', 'onder')) # hier gelijk en ongelijk toevoegen

class Trigger(models.Model):
    name = models.CharField(max_length=100,verbose_name='naam')
    description = models.TextField(blank=True)
    hilo = models.CharField(max_length=1,choices=HILO,default='>',verbose_name='grens',help_text='onder of bovengrens')
    level = models.FloatField(verbose_name='grenswaarde')
    freq = models.CharField(max_length=8,choices=FREQ,blank=True, null=True, verbose_name = 'frequentie', help_text='frequentie voor resampling')
    how = models.CharField(max_length=16,choices=HOW,blank=True, null=True, verbose_name = 'methode', help_text='methode van aggregatie')
    window = models.IntegerField(default=1,verbose_name='groep',help_text='grootte van de groep')
    count = models.IntegerField(default=1,verbose_name='aantal',help_text='minimum aantal punten')
            
    def __unicode__(self):
        return self.name

    def select(self,series,**kwargs):
        ''' select events from a time series '''
        s = series.to_pandas(**kwargs)
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

class Target(models.Model):
    user = models.ForeignKey(User)
    cellphone = models.CharField(max_length=12)
    email = models.EmailField()
    
    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = 'ontvanger'
        
ACTION_IGNORE = 0
ACTION_EMAIL = 1
ACTION_SMS = 2
ACTIONS = ((ACTION_IGNORE, 'negeren'),
           (ACTION_EMAIL, 'email'),
           (ACTION_SMS, 'sms'),
           )
    
class Event(models.Model):
    trigger = models.ForeignKey(Trigger)
    series = models.ForeignKey(Series,verbose_name='tijdreeks')
    target = models.ForeignKey(Target,verbose_name='ontvanger')
    action = models.IntegerField(default = ACTION_IGNORE, choices=ACTIONS, verbose_name = 'actie')
    message = models.TextField(blank=True,null=True,verbose_name='Standaard bericht')

    def __unicode__(self):
        return self.trigger.name

    def format_message(self, date, value, html=False):
        if html:
            return '<p>{evt} was triggered on {date}<br/>Details: {ser} = {value}</p>'.format(evt=str(self.trigger), ser=str(self.series),date=date,value=value)
        else:
            return '{evt} was triggered on {date}\r\nDetails: {ser} = {value}'.format(evt=str(self.trigger), ser=str(self.series),date=date,value=value)

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