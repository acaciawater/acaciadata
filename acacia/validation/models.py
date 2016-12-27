from django.db import models
from django.contrib.auth.models import User
from acacia.data.models import Series, DataPoint
import pandas as pd
import numpy as np
import itertools
from polymorphic.models import PolymorphicModel

COMPARE_CHOICES = (
    ('GT', 'boven'), 
    ('LT', 'onder'),
    ('EQ', 'gelijk'),
    ('NE', 'ongelijk'))

class BaseRule(PolymorphicModel):
    ''' Basic validation rule '''
    class Meta:
        verbose_name = 'regel'
        
    name = models.CharField(max_length=50,verbose_name='naam')
    description = models.TextField(blank=True,verbose_name='omschrijving')
    comp = models.CharField(max_length=2, choices=COMPARE_CHOICES, default='GT',verbose_name='vergelijking')

    def compare(self,a,b):
        if self.comp == 'GT':
            return a > b
        elif self.comp == 'LT':
            return a < b
        elif self.comp == 'EQ':
            return a == b
        elif self.comp == 'NE':
            return a != b
        return None

    def apply(self,target):
        return self.compare(target, 0)
    
    def __unicode__(self):
        return self.name

class ValueRule(BaseRule):
    ''' validation rule with set limits '''
    class Meta:
        verbose_name = 'Vaste grens'
        
    value = models.FloatField(null=True,blank=True,default=None,verbose_name='waarde',help_text='validatiewaarde waarde')

    def apply(self,target):
        return self.compare(target, self.value)

class SeriesRule(BaseRule):
    class Meta:
        verbose_name = 'Tijdreeks'

    ''' compare with other series '''
    series = models.ForeignKey(Series,null=True,blank=True,default=None,verbose_name='tijdreeks', help_text='validatie tijdreeks')
    def apply(self,target):
        ''' apply this rule on a target series '''
        return self.compare(target, self.series)

class NoDataRule(BaseRule):
    class Meta:
        verbose_name = 'Geen gegevens'
        
    ''' counts measurements in timeslot ''' 
    slot = models.CharField(max_length=4,default='D')
    count = models.PositiveIntegerField(default=1)
    def apply(self, target):
        counts = target.resample(self.slot).count() 
        return counts >= self.count

class OutlierRule(BaseRule):
    class Meta:
        verbose_name = 'Uitbijter'

    ''' identifies outliers based on standard deviation and mean ''' 
    tolerance = models.FloatField(default=3,verbose_name = 'tolerantie', help_text = 'gemiddelde plus of min x maal de standaardafwijking')
    def apply(self, target):
        devi = abs(target-target.mean()) / target.std()
        return devi <= self.tolerance
 
class DiffRule(BaseRule):
    class Meta:
        verbose_name = 'Lokale uitbijter'
    
    ''' identifies outliers based on difference and standard deviation ''' 
    tolerance = models.FloatField(default=3,verbose_name = 'tolerantie', help_text = 'verschil plus of min x maal de standaardafwijking')
    def apply(self, target):
        devi = abs(target.diff()) / target.std()
        test = devi[devi > self.tolerance]
        print test.count()
        return devi <= self.tolerance
 
# class Rule(models.Model):
#     ''' Validation rule '''
#     class Meta:
#         verbose_name = 'regel'
#         verbose_name_plural = 'regels'
#         
#     name = models.CharField(max_length=50,verbose_name='naam')
#     description = models.TextField(blank=True,verbose_name='omschrijving')
#     value = models.FloatField(null=True,blank=True,default=None,verbose_name='waarde',help_text='vaste validatiewaarde waarde (criterium)')
#     series = models.ForeignKey(Series,null=True,blank=True,default=None,verbose_name='tijdreeks', help_text='validatie tijdreeks')
#     comp = models.CharField(max_length=2, choices=COMPARE_CHOICES, default='GT',verbose_name='vergelijking')
#  
#     def apply(self,target):
#         ''' apply this rule on a target series '''
#         '''TODO: laatste waarde langer dan x dagen geleden '''
#         def compare(a,b):
#             if self.comp == 'GT':
#                 return a > b
#             elif self.comp == 'LT':
#                 return a < b
#             elif self.comp == 'EQ':
#                 return a == b
#             elif self.comp == 'NE':
#                 return a != b
#             return None
# 
#         rhs = self.series.to_pandas() if self.series else self.value
#         result = compare(target, rhs)
#         return result
#     
#     def __unicode__(self):
#         return self.name

class ValidPoint(models.Model):
    # the original datapoint
    point = models.ForeignKey(DataPoint)
    # the validation that was applied
    validation = models.ForeignKey('Validation')
    # validated value
    value = models.FloatField(null=True)

class Validation(models.Model):
    
    class Meta:
        verbose_name = 'validatie'
        verbose_name_plural = 'validaties'
        
    series = models.ForeignKey(Series,verbose_name = 'tijdreeks')
    rules = models.ManyToManyField(BaseRule, verbose_name = 'validatieregels')
    
    def apply(self, **kwargs):
        points = self.series.filter_points(**kwargs).order_by('date')
        index, data = zip(*[(p.date,p.value) for p in points])
        series = pd.Series(data,index)

        for rule in self.rules.all():
            series = series.where(rule.apply(series),other=None)

        valid_points = [ValidPoint(validation=self,point=p,value=v) for p,v in itertools.izip(points,series.values)]
        return valid_points
    
    def persist(self, **kwargs):
        pts = self.apply(**kwargs)
        self.validpoint_set.all().delete()
        self.validpoint_set.bulk_create(pts)
        return pts
    
    def __unicode__(self):
        return unicode(self.series)
    
VALIDATION_STATUS = (
    ('P','pending'),
    ('A','accepted'),
    ('R','rejected'),
    )
  
class ValidationResult(models.Model):
    
    class Meta:
        verbose_name = 'resultaat'
        verbose_name_plural = 'resultaten'
        
    validation = models.ForeignKey(Validation,verbose_name = 'validatie')
    begin = models.DateTimeField()
    end = models.DateTimeField()
    xlfile = models.FileField(upload_to='valid')
    user = models.ForeignKey(User)
    remarks = models.TextField(blank=True,null=True)
 
    def __unicode__(self):
        return self.validation
     
