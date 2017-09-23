from django.db import models, transaction
from django.contrib.auth.models import User
from acacia.data.models import Series
from django.core.urlresolvers import reverse
import numpy as np
import pandas as pd
from polymorphic.models import PolymorphicModel
import logging
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.templatetags.admin_list import results

logger = logging.getLogger(__name__)

COMPARE_CHOICES = (
    ('GT', 'boven'), 
    ('LT', 'onder'),
    ('EQ', 'gelijk'),
    ('NE', 'ongelijk'))

class BaseRule(PolymorphicModel):
    ''' Basic validation rule (compares a time series with zero)'''
    class Meta:
        verbose_name = 'regel'
        ordering = ('name',)
        
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
        return (target,self.compare(target, 0))
    
    def __unicode__(self):
        return self.name
    
    
class ValueRule(BaseRule):
    ''' validation rule with set limits (compares a time series with fixed numeric value) '''
    class Meta:
        verbose_name = 'Vaste grens'
        
    value = models.FloatField(null=True,blank=True,default=None,verbose_name='waarde',help_text='validatiewaarde waarde')

    def apply(self,target):
        return (target,self.compare(target, self.value))

class SeriesRule(BaseRule):
    ''' compares series with other series (compares target with constant + series * factor) '''
    class Meta:
        verbose_name = 'Tijdreeks'

    series = models.ForeignKey(Series,null=True,blank=True,default=None,verbose_name='tijdreeks', help_text='validatie tijdreeks')
    constant = models.FloatField(default=0)
    factor = models.FloatField(default=1)
    
    def apply(self,target):
        series = self.series.to_pandas()
        series = series.reindex(target.index,method='nearest')
        return (target,self.compare(abs(target * self.factor + self.constant), series))
        #return (target,self.compare(abs(target * self.factor - self.series), self.constant))

SLOT_CHOICES = (
    ('T', 'minuut'),
    ('H', 'uur'),
    ('D', 'dag'),
    ('W', 'week'),
    ('M', 'maand'),
    )
class NoDataRule(BaseRule):
    ''' Rule that checks a time series for number of measurements in specified time span (e.g. at least 6 values per day) '''
    class Meta:
        verbose_name = 'Aantal'
        
    slot = models.CharField(max_length=10,default='D',choices=SLOT_CHOICES,verbose_name='Frequentie')
    count = models.PositiveIntegerField(default=1,verbose_name='Aantal')
    
    def apply(self, target):
        # count points in every time slot
        bins = target.resample(self.slot).count()
        # find missing data
        missing = bins[bins==0].astype(np.object)
        missing[:] = None
        # insert missing points in target
        target = target.append(missing).sort_index()

        valid = self.compare(bins,self.count)
        tolerance = valid.index[1] - valid.index[0] if valid.size > 1 else 3600*24*1000 # default: 1 day
        # align validated bins with target
        result = valid.reindex(target.index,method='nearest',tolerance=tolerance)
        return (target, result)

class SlotRule(BaseRule):
    ''' Rule that checks a time series for a single measurements in specified time span'''
    class Meta:
        verbose_name = 'Interval'
        
    count = models.PositiveIntegerField(default=1,verbose_name='Aantal')
    slot = models.CharField(max_length=4,default='D',choices=SLOT_CHOICES,verbose_name='Eenheid')

    def apply(self, target):
        # count points in every time slot
        slot = '%d%s' % (self.count,self.slot)
        bins = target.resample(slot).count()
        # find missing data
        bins=bins.astype(np.object)
        missing = bins[bins==0].replace(0,None)
        
        # insert missing points in target
        target = target.append(missing).sort_index()

        valid = bins[bins>0]
        tolerance = valid.index[1] - valid.index[0] if valid.size > 1 else 3600*24*1000 # default: 1 day
        # align validated bins with target
        result = valid.reindex(target.index,method='nearest',tolerance=tolerance)
        return (target, result)
    
class OutlierRule(BaseRule):
    ''' Finds  outliers based on standard deviation and mean ''' 
    class Meta:
        verbose_name = 'Uitbijter'

    tolerance = models.FloatField(default=3,verbose_name = 'tolerantie', help_text = 'gemiddelde plus of min x maal de standaardafwijking')
    
    def apply(self, target):
        std = target.std() * self.tolerance
        dev = (target-target.mean()).abs()
        return (target,self.compare(dev,std))

class RollingRule(OutlierRule):
    ''' Finds  outliers based on rolling standard deviation and mean ''' 
    class Meta:
        verbose_name = 'Locale Uitbijter'

    count = models.PositiveIntegerField(default=3,verbose_name='Aantal punten')
    
    def apply(self, target):
        roll = target.rolling(window=self.count,center=True)
        mean = roll.median().fillna(method='bfill').fillna(method='ffill')
        std = target.std() * self.tolerance
        dev = (target-mean).abs()
        return (target,self.compare(dev,std))
 
class DiffRule(BaseRule):
    ''' Finds local outliers based on difference between successive points and standard deviation ''' 
    class Meta:
        verbose_name = 'Lokale verandering'
    
    tolerance = models.FloatField(default=3,verbose_name = 'tolerantie', help_text = 'verschil plus of min x maal de standaardafwijking')
    
    def apply(self, target):
        std = target.std() * self.tolerance
        dev = target.diff().abs()
        if dev.size > 0:
            dev.iloc[0] = 0
        return (target,self.compare(dev,std))

class ChangeRule(BaseRule):
    ''' Finds local outliers based on percent difference in a period ''' 
    class Meta:
        verbose_name = 'Verandering'
    
    freq = models.CharField(max_length=4,default='D',choices=SLOT_CHOICES,verbose_name='frequentie')
    periods = models.PositiveIntegerField(default=1,verbose_name = 'periode', help_text = 'aantal periodes vooruit')
    change = models.FloatField(default=0, verbose_name='verandering', help_text='procentuele verandering')    
    
    def apply(self, target):
        ch = target.pct_change(periods=self.periods,freq = self.freq)
        return (target,self.compare(ch,self.change))

class ScriptRule(BaseRule):
    ''' Validation rule based on user defined python script.
    The script must set a local variable named result: 
    a tuple consisting of the target series and a boolean series with the validation result '''
    
    class Meta:
        verbose_name = 'Python script'

    script = models.TextField(default = "print 'running validation script ' + unicode(self)\nresult = (target,self.compare(target, 0))")
    
    def apply(self, target):
        try:
            var = {'self': self, 'target': target}
            ret = {}
            exec (self.script, var, ret)
            if not 'result' in ret:
                raise ValueError('User script must set local variable result')
            result = ret['result']

            if isinstance(result, tuple):
                return result
            else:
                return (target, result)
            
        except Exception as e:
            raise e

class ValidPoint(models.Model):
    ''' A datapoint that has passed a validation rule '''
    validation = models.ForeignKey('Validation')
    date = models.DateTimeField()
    value = models.FloatField(default=None,null=True)

class Validation(models.Model):
    
    class Meta:
        verbose_name = 'validatie'
        verbose_name_plural = 'validaties'
        ordering = ('series',)
        
    series = models.OneToOneField(Series,verbose_name = 'tijdreeks')
    rules = models.ManyToManyField(BaseRule, verbose_name = 'validatieregels',through='RuleOrder',related_name='validations')
    users = models.ManyToManyField(User,blank=True,help_text='Gebruikers die emails ontvangen over validatie')
    valid = models.NullBooleanField(default=None,verbose_name='Valide')
    validated = models.BooleanField(default=False,verbose_name='Gevalideerd')
    last_validation = models.DateTimeField(null=True,blank=True,default=None,verbose_name='Laatste validatie')

    valid.boolean = True
    validated.boolean = True
    
    def get_absolute_url(self):
        return reverse('validation:validation-detail', args=[self.id])

    def results(self):
        ''' returns dict with rules and results '''
        results = {r:None for r in self.rules.all()}
        for s in self.subresult_set.all():
            results[s.rule] = s
        return results
    
    def iter_exceptions(self):
        for v in self.validpoint_set.filter(value__isnull=True):
            yield v.point

    def filter_points(self, **kwargs):
        ''' filter valid points on date '''
        start = kwargs.get('start', None)
        stop = kwargs.get('stop', None)
        if start is None and stop is None:
            return self.validpoint_set.all()
        return self.validpoint_set.filter(date__range=[start or self.series.van(),stop or self.series.tot()]).order_by('date')

    def select_points(self,**kwargs):
        ''' select (and possibly create) valid points '''
        points = self.filter_points(**kwargs)
        if points.exists():
            addpoints = self.series.datapoints.filter(date__gt=points.last().date)
        else:
            addpoints = self.series.filter_points(**kwargs)
        if addpoints.exists():
            self.validpoint_set.bulk_create([ValidPoint(validation=self,date=p.date,value=p.value) for p in addpoints])
            points = self.filter_points(**kwargs)
        return points
    
    def to_pandas(self, **kwargs):
        try:
            index,data = zip(*self.filter_points(**kwargs).values_list('date','value'))
            return pd.Series(data,index).sort_index()
        except:
            return pd.Series()

    @property        
    def invalid_points(self):
        return self.validpoint_set.filter(value__isnull=True)

    @property        
    def num_invalid_points(self):
        return self.invalid_points.count()

    def check_valid(self):
        ''' checks validity '''
        if self.check_validated():
            self.valid = not self.invalid_points.exists()
        else:
            self.valid = None
        return self.valid

    def check_validated(self):
        ''' checks if was validated ''' 
        self.validated = self.validpoint_set.exists()
        return self.validated
    
    def apply(self, **kwargs):
        ''' apply validation and return validated points '''
        
        # retrieve both existing and new points
        points = self.select_points(**kwargs).order_by('date')
        
        # create pandas time series from points
        if points and points.exists():
            index, data = zip(*[(p.date, p.value) for p in points])
            series = pd.Series(data,index)
            series = series.groupby(series.index).last()
    
            numinvalid = 0
            result = None
            logger.debug('Validating {}: {} rules'.format(self.series, self.rules.count()))
            self.subresult_set.all().delete()
            for ro in self.ruleorder_set.all():
                rule = ro.rule
                series, valid = rule.apply(series)
                valid = valid.groupby(valid.index).last()
                if result is None:
                    # save result
                    result = valid
                else:
                    # update the result
                    result = result.where(valid,other=None)
    
                invalid = valid[valid==False]
                invalid_count = invalid.count()
                numinvalid += invalid_count
                valid_count = valid.count() - invalid_count
    
                if invalid_count:
                    first = invalid.index[0]
                    logger.warning('validation {}, rule "{}" failed at {}'.format(self.series,rule,first))
                else:
                    first = None
                    logger.info('validation {}, rule "{}" passed'.format(self.series,rule))
                self.subresult_set.create(rule=rule,valid=valid_count,invalid=invalid_count,first_invalid=first)
    
            # set values to None where validation failed
            series = series.where(result,other=None)
            valid_points = [ValidPoint(validation=self,date=p[0],value=p[1]) for p in series.iteritems()]
            if numinvalid:
                logger.warning('Validation failed for {}, first occurrence = {}'.format(self.series, invalid.index[0]))
            else:
                logger.info('Validation {} passed'.format(self.series))
            return valid_points
        else:
            logger.warning("Validation {}: no datapoints".format(self.series))
            return []

    def reset(self):
        ''' resets this validation: removes all points and results '''
        if self.has_result():
            self.result.delete()
        self.subresult_set.all().delete()
        self.validpoint_set.all().delete()
        self.last_validation = None
        self.check_valid()
        self.save()
        
    def persist(self, **kwargs):
        ''' apply validation and dump points to database '''
        pts = self.apply(**kwargs)
        with transaction.atomic():
            # replace ALL validated points
            self.validpoint_set.all().delete()
            self.validpoint_set.bulk_create(pts)
        self.last_validation = datetime.datetime.now()
        self.check_valid()
        self.save()
        return pts
    
    def has_result(self):
        try:
            return self.result is not None
        except ObjectDoesNotExist:
            return False
        
    def __unicode__(self):
        return unicode(self.series)

class RuleOrder(models.Model):
    ''' order of a rule in a validation '''
    rule = models.ForeignKey(BaseRule, on_delete=models.CASCADE)
    validation = models.ForeignKey(Validation, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Regel'
        ordering = ['order']
         
class SubResult(models.Model):
    ''' Result of applying a single validation rule ''' 
    class Meta:
        verbose_name = 'tussenresultaat'
        verbose_name_plural = 'tussenresultaten'

    validation = models.ForeignKey(Validation)
    rule = models.ForeignKey(BaseRule)
    valid = models.PositiveIntegerField()
    invalid = models.PositiveIntegerField()
    first_invalid = models.DateTimeField(null=True)
    message = models.TextField(null=True,blank=True)
    
    def __unicode__(self):
        return '{}:{}'.format(self.validation, self.rule)
  
class Result(models.Model):
    ''' Result of a validation, including uploaded datafile of a user '''
    class Meta:
        verbose_name = 'resultaat'
        verbose_name_plural = 'resultaten'
        
    validation = models.OneToOneField(Validation,verbose_name = 'validatie')
    begin = models.DateTimeField()
    end = models.DateTimeField()
    xlfile = models.FileField(upload_to='valid',blank=True,null=True)
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True,verbose_name='uploaded')
    remarks = models.TextField(blank=True,null=True)
    valid = models.BooleanField(default = False)

    def __unicode__(self):
        return unicode(self.validation)
