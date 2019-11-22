'''
Created on Nov 15, 2019

@author: theo
'''
import logging

from django.conf import settings

from acacia.data.models import Generator
from acacia.meetnet.models import Network, Well, Handpeilingen, \
    Datalogger, LoggerDatasource, DIVER_TYPES
from acacia.meetnet.util import register_well, register_screen
from datetime import datetime
from dateutil.parser import parser, parse
import pandas as pd
import os
import pytz

logger = logging.getLogger(__name__)

def handle_registration_files(request):
    from django.contrib.gis.geos import Point
    from zipfile import ZipFile

    # create dedicated log file
    folder = os.path.join(settings.LOGGING_ROOT, request.user.username)
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = 'import_{:%Y%m%d%H%M}.log'.format(datetime.now())
    logfile = os.path.join(folder, filename)
    logurl = settings.LOGGING_URL + request.user.username + '/' + filename
    handler = logging.FileHandler(logfile,'w')
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler)

    user = request.user
    network = Network.objects.first()
    tz = pytz.timezone('Europe/Amsterdam')
    
    metadata = request.FILES['metadata']
    logger.info('Metadata: {}'.format(metadata.name))
    # TODO: save file somewhere
    
    archive = request.FILES.get('fotos')
    logger.info('Fotos: {}'.format(archive.name if archive else 'geen'))
    fotos = ZipFile(archive) if archive else None

    archive = request.FILES.get('boorstaten')
    logger.info('Boorstaten: {}'.format(archive.name if archive else 'geen'))
    logs = ZipFile(archive) if archive else None
    
    df = pd.read_excel(metadata,'Putgegevens')
    for _index, row in df.iterrows():

        def get(col, astype=str):
            ''' get a value from a cell in the spreadsheet, converting to specified type. 
                returns None when conversion fails or cell is blank, NaN, NaT or null
            '''
            value = row.get(col)
            if pd.isnull(value): 
                return None
            if astype:
                try:
                    value = astype(value)
                except:
                    return None
            return value
        
        id = get('ID')
        x = get('X',float)
        y = get('Y',float)
        pobox = get('Postcode')
        street = get('Straat')
        housenumber= get('Huisnummer')
        town = get('Plaats')
        remarks = get('Opmerkingen locatie')
        date = get('Constructiedatum')
        surface = get('Maaiveld')
        owner = get('Eigenaar')
        coords = Point(x,y,srid=28992)
        coords.transform(4326)
        try:
            well, created = Well.objects.update_or_create(network=network, name=id, defaults = {
                'location': coords,
                'description': remarks,
                'maaiveld': surface,
                'date': date,
                'owner': owner,
                'straat': street,
                'huisnummer': housenumber,
                'postcode': pobox,
                'plaats': town
                })
            if created:
                logger.info('Metadata voor put {} aangemaakt'.format(id))
                register_well(well)
            else:
                logger.info('Metadata voor put {} bijgewerkt'.format(id))
        except Exception as e:
            logger.exception(e)
            continue
        nr = get('Filternummer',int)
        refpnt = get('Bovenkant buis',float)
        top = get('Bovenkant filter m-MV',float)
        bottom = get('Onderkant filter m-MV',float)
        diameter = get('Diameter buis',float)
        material = get('Materiaal')
        screen, created = well.screen_set.update_or_create(nr=nr, defaults = {
            'refpnt': refpnt,
            'top': top,
            'bottom': bottom,
            'diameter': diameter,
            'material': material,
            })
        if created:
            logger.info('Metadata voor filter {} aangemaakt'.format(screen))
            register_screen(screen)
        else:
            logger.info('Metadata voor filter {} bijgewerkt'.format(screen))

        hand, created = Handpeilingen.objects.update_or_create(screen=screen,defaults={
            'refpnt': 'bkb',
            'user': user,
            'mlocatie': screen.mloc,
            'name': '{} HAND'.format(screen),
            'unit': 'm',
            'type': 'scatter',
            'timezone': settings.TIME_ZONE
        })
        if created:
            logger.info('Metadata voor handpeilingen {} aangemaakt'.format(screen))
        else:
            logger.info('Metadata voor handpeilingen {} bijgewerkt'.format(screen))

        serial = get('Logger ID',None)
        if serial:
            if type(serial) == float:
                serial = str(int(serial))
            model = get('Logger type')
            if not model:
                logger.error('Logger type ontbreekt')
                continue
    
            generator = Generator.objects.get(name='Ellitrack' if model.lower().startswith('elli') else 'Schlumberger')
            # determine diver code from model name
            choice = filter(lambda x: x[1].lower() == model.lower(), DIVER_TYPES)
            if choice:
                code = choice[0][0]
            else:
                logger.error('Onbekend logger type: {}'.format(model))
                continue
            datalogger, created = Datalogger.objects.get_or_create(serial=serial,defaults={'model':code})
            if created:
                logger.info('Logger {} aangemaakt'.format(serial))
        
            start = get('Datum installatie',None)
            if start:
                start = tz.localize(start)
            depth = get('Kabellengte', float)
            if depth:
                depth /= 100.0
            defaults = {
                'screen': screen,
                'start_date' : start,
                'refpnt': screen.refpnt,
                'depth': depth,
                }
            pos, created = datalogger.loggerpos_set.update_or_create(logger=datalogger,defaults=defaults)
            if created:
                logger.info('Logger {} geinstallleerd in filter {}'.format(datalogger, screen))
            else:
                logger.info('Metadata van logger {} in filter {} bijgewerkt'.format(datalogger, screen))

            ds, created = LoggerDatasource.objects.update_or_create(
                logger = datalogger,
                name = serial,
                defaults={'description': '{} datalogger {}'.format(model, serial),
                          'meetlocatie': screen.mloc,
                          'timezone': 'Europe/Amsterdam',
                          'user': user,
                          'generator': generator,
                          'url': settings.FTP_URL,
                          'username': settings.FTP_USERNAME,
                          'password': settings.FTP_PASSWORD,
                          'config': '{{"logger": "{}"}}'.format(serial)
                          })
            if created:
                ds.locations.add(screen.mloc)
                logger.info('Gegevensbron {} aangemaakt'.format(ds))
            else:
                logger.info('Gegevensbron {} bijgewerkt'.format(ds))
                
            if fotos:    
                for nr in range(1,6):
                    name = get('Foto %d'%nr)
                    if name:
                        try:
                            with fotos.open(name,'r') as foto:
                                well.add_photo(name,foto)
                                logger.info('Foto toegevoegd: {}'.format(name))
                        except Exception as e:
                            logger.error('Kan foto niet toevoegen: {}'.format(e))
                    else:
                        break                            
            
            if logs:
                name = get('Boorstaat')
                if name:
                    try:
                        with logs.open(name) as log:
                            well.set_log(name,log)
                            logger.info('Boorstaat toegevoegd: {}'.format(name))
                    except Exception as e:
                        logger.error('Kan boorstaat niet toevoegen: {}'.format(e))
            
    return logurl
