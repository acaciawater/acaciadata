from acacia.data.util import toRD, WGS84 
from django.contrib.gis.geos import Point
from acacia.data.models import Project, Generator
from acacia.data.generators import FEWS
from django.contrib.auth.models import User 
from django.core.management.base import BaseCommand, CommandError
import requests
from pydoc import describe
from django.conf import settings

username = settings.FEWSUSERNAME
password = settings.FESWSPASSWORD
headers = {'username':username,'password':password}
error_message = 'WNS1400.1h, H.gewogen.toekomst.ruw, Q.meting, H.streef, H.gewogen, H.gewogen.toekomst, Q.advies, H.meting, Q.berekend, WNS9040, WNS2368, WNS2369.h, WNS9688, WNS2369, CL.berekend, UNKNOWN, H.niveau, EGVms_cm.meting, O2.geh.meting, O2.sat.meting, WNS1923, 111TClTol (B)'


def get_locations_and_timeseries(headers, string):
    '''
    expects username and password in headers, and a string to search
    valid search strings are:   u'WNS1400.1h', u'H.gewogen.toekomst.ruw',
                                u'Q.meting', u'H.streef', u'H.gewogen', 
                                u'H.gewogen.toekomst', u'Q.advies', u'H.meting', 
                                u'Q.berekend', u'WNS9040', u'WNS2368', u'WNS2369.h', 
                                u'WNS9688', u'WNS2369', u'CL.berekend', u'UNKNOWN', 
                                u'H.niveau', u'EGVms_cm.meting', u'O2.geh.meting',
                                u'O2.sat.meting', u'WNS1923', u'111TClTol (B)']
    returns a structured dictionary with all locations and corresponding timeseries for HHNK only  
    '''
    query = {'search' : string}
    url = 'https://api.ddsc.nl/api/v2/timeseries/'
    result={}
    while url != None:
            response = requests.get(url = url, headers = headers, params=query)
            json = response.json()
            for x in (json['results']):
                if x['location']['organisation']['name'] == 'HHNK':
                    if ', ' in x['location']['name']:
                        ml_name = x['location']['name'].split(', ')[0]
                        ml_ds_desc = x['parameter_referenced_unit']['parameter_short_display_name']+', '+x['location']['name']
                    else:
                        ml_name = x['location']['name']
                        ml_ds_desc = x['parameter_referenced_unit']['parameter_short_display_name']
                    ml_ds_name = x['name']+' '+x['location']['name']
                    ml_latlon = x['location']['geometry']['coordinates']
                    rd = Point(x=ml_latlon[0],y=ml_latlon[1],srid=WGS84)  
                    #rd = toRD(rd)                  
                    ml_ds_unit = x['parameter_referenced_unit']['referenced_unit_short_display_name']
                    ml_ds_url = x['url']
                    datasource = [{ml_ds_name:{'descrition':ml_ds_desc,'unit':ml_ds_unit,'url':ml_ds_url}}]
                    result[ml_name]= result.get(ml_name, {'location':rd})
                    try:
                        result[ml_name]['datasources'] += datasource
                    except:
                        result[ml_name]['datasources'] = datasource
            url = json['next']
            query = None
    return result

class Command(BaseCommand):
    args = ''
    help = 'FEWS timeseries update'
    
    def add_arguments(self, parser):
        parser.add_argument('--query',
                action='store',
                type = str,
                dest = '--query',
                default = None,
                help = 'lizard filter')

    def handle(self, *args, **options):
        user = User.objects.get(username='stephane')
        query = options['--query']
        dictio = get_locations_and_timeseries(headers, query)
        project_name = 'HHNKmeet'
        proj_descr = 'HHNK FEWS db'
        project, created = Project.objects.get_or_create(name = project_name,description = proj_descr)
        # create projectlocatie 
        pl_name = 'HHNK_HQ'
        HHNK_HQ_loc = Point(x=4.8232246, y=52.6691314, srid=WGS84)
        #HHNK_HQ_loc = toRD(HHNK_HQ_loc)
        HHNK_HQ_descr = 'Hoofdkantoor HHNK'
        ploc, created = project.projectlocatie_set.get_or_create(name = pl_name, description=HHNK_HQ_descr, defaults = {'location': HHNK_HQ_loc })
        # create meetlocatie
        for ml in dictio.keys():
            mloc, created = ploc.meetlocatie_set.get_or_create(name=ml, description = ml, defaults = {'location': dictio[ml]['location']})
            for ds in dictio[ml]['datasources']:
                #create datasources
                name = ds.keys()[0]
                gen = Generator.objects.get(name='FEWS')
                ds_descr = ''
                ds, created = mloc.datasources.get_or_create(name=name, defaults = {'user':user, 'generator':gen, 'description':ds_descr, 'url':ds[name]['url']})



if __name__ == "__main__":
    c = Command()
    c.handle(query='EGVms_cm.meting')

