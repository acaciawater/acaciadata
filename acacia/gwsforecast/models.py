'''
Created on Nov 16, 2016

@author: stephane
'''
import binascii, json, StringIO
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from acacia.data.models import Datasource, Series, SourceFile, MeetLocatie
from acacia.data.generators.generic import GenericCSV
from acacia.gwsforecast import gws_forecaster

gws_forecaster

class GWSForecast(Datasource):
    '''
    usese the location of itself to get the data from knmi if any of the series apart from hist_gws are empty
    passes the location to the generator
    hist_gws,hist_ev,hist_pt,forec_et,forec_pt,forec_tmp
    '''
    hist_gws = models.ForeignKey(Series)
    hist_ev = models.ForeignKey(Series,related_name='hist_ev')
    hist_pt = models.ForeignKey(Series,related_name='hist_pt')
    forec_et = models.ForeignKey(Series,related_name='forec_et')
    forec_pt = models.ForeignKey(Series,related_name='forec_pt')
    forec_tmp = models.ForeignKey(Series,related_name='forec_tmp')
    
#     hist_ev = models.ForeignKey(Series,null=True,blank=True,related_name='hist_ev')
#     hist_pt = models.ForeignKey(Series,null=True,blank=True,related_name='hist_pt')
#     forec_et = models.ForeignKey(Series,null=True,blank=True,related_name='forec_et')
#     forec_pt = models.ForeignKey(Series,null=True,blank=True,related_name='forec_pt')
#     forec_tmp = models.ForeignKey(Series,null=True,blank=True,related_name='forec_tmp')
#     
    
    def download(self, start=None):
        logger = self.getLogger()
        options = { 'hist_gws': self.hist_gws,'hist_ev':self.hist_ev,'hist_pt':self.hist_pt,
                    'forec_et':self.forec_et,'forec_pt':self.forec_pt,'forec_tmp':self.forec_tmp}
         
        if self.generator is None:
            logger.error('Cannot download datasource %s: no generator defined' % (self.name))
            return None
         
        gen = self.get_generator_instance()
        
        if gen is None:
            logger.error('Cannot download datasource %s: could not create instance of generator %s' % (self.name, self.generator))
            return None
        
        if self.meetlocatie:
            #lonlat = self.meetlocatie.latlon() # does not initialize geo object manager
            loc = MeetLocatie.objects.get(pk=self.meetlocatie.pk)
            lonlat = loc.latlon()
            options['lonlat'] = (lonlat.x,lonlat.y)
        
        try:
            # merge options with config
            config = json.loads(self.config)
            options = dict(options.items() + config.items())
        except Exception as e:
            logger.error('Cannot download datasource %s: error in config options. %s' % (self.name, e))
            return None
        
        if start is not None:
            # override starting date/time
            options['start'] = start
        elif not 'start' in options:
            # incremental download
            options['start'] = self.stop()
        try:
            files = []
            crcs = {f.crc:f.file for f in self.sourcefiles.all()}
        
#         return Datasource.download(self, start=start)
            def callback(result):
                    for filename, contents in result.iteritems():
                        crc = abs(binascii.crc32(contents))
                        if crc in crcs:
                            logger.warning('Downloaded file %s ignored: identical to local file %s' % (filename, crcs[crc].file.name))
                            continue
                        try:
                            sourcefile = self.sourcefiles.get(name=filename)
                        except:
                            sourcefile = SourceFile(name=filename,datasource=self,user=self.user)
                        sourcefile.crc = crc
                        contentfile = ContentFile(contents)
                        try:
                            sourcefile.file.save(name=filename, content=contentfile)
                            logger.debug('File %s saved to %s' % (filename, sourcefile.filepath()))
                            crcs[crc] = sourcefile.file
                            files.append(sourcefile)
                        except Exception as e:
                            logger.exception('Problem saving file %s: %s' % (filename,e))
     
            options['callback'] = callback
            results = gen.download(**options)
    
        except Exception as e:
            logger.exception('Error downloading datasource %s: %s' % (self.name, e))
            return None            
        logger.info('Download completed, got %s file(s)', len(results))
        self.last_download = timezone.now()
        self.save(update_fields=['last_download'])
        return files


class GWSGenerator(GenericCSV):
    '''
    embeds the model of miriam
    overwrite the downloadfunction so that it's output is the forecasted gws and the historical one
    creates a voorspelde gws als berekende reeks
    if no values in 5 series, get it form knmi on basis of location
    '''
    
    def download(self, **kwargs):
        result = {}
        callback = kwargs.get('callback', None)
        hist_gws = kwargs.get('hist_gws', None)
        hist_ev = kwargs.get('hist_ev', None)
        hist_pt = kwargs.get('hist_pt', None)
        forec_et = kwargs.get('forec_et', None)
        forec_pt = kwargs.get('forec_pt', None)
        forec_tmp = kwargs.get('forec_tmp', None)
        
        response =  gws_forecaster.gws_forecast(hist_gws, hist_ev, hist_pt, forec_et, forec_pt, forec_tmp)
        s = StringIO.StringIO()
        response.to_csv(s)
        response_string = s.getvalue()
        
        filename = 'forecasted_' + hist_gws.name +'.csv'
        result[filename] = response_string
        if callback is not None:
            callback(result)        
        return result
    
