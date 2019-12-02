'''
Created on Nov 15, 2019

@author: theo
'''
from datetime import datetime, date, timedelta
import logging
import os

from django.conf import settings
from django.contrib.gis.geos import Point
import pytz

from acacia.data.models import Generator
from acacia.meetnet.models import Network, Well, Datalogger, LoggerDatasource, DIVER_TYPES, Screen,\
    Handpeilingen
from acacia.meetnet.util import register_well, register_screen
import pandas as pd
from zipfile import ZipFile
import dateutil


logger = logging.getLogger(__name__)

def parse_date(cell):
    if cell is not None:
        if isinstance(cell,(datetime,date)):
            return cell
        if len(cell)>0:
            try:
                return dateutil.parser.parse(cell)
            except:
                pass
    return None

def import_metadata(request, sheet='Putgegevens'):
    tz =pytz.timezone('Europe/Amsterdam')
    network = Network.objects.first()
    
    book = request.FILES['metadata']
    book.seek(0)
    logger.info('Metadata: {}'.format(book.name))
    # TODO: save file somewhere
    
    archive = request.FILES.get('fotos')
    logger.info('Fotos: {}'.format(archive.name if archive else 'geen'))
    fotos = ZipFile(archive) if archive else None

    archive = request.FILES.get('boorstaten')
    logger.info('Boorstaten: {}'.format(archive.name if archive else 'geen'))
    logs = ZipFile(archive) if archive else None

#     df = pd.read_excel(book, sheet, converters={'Constructiedatum': date_parser, 'Datum installatie': date_parser})
    df = pd.read_excel(book, sheet, parse_dates=['Constructiedatum', 'Datum installatie'])
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
        
        id = get('ID').strip()
        logger.info('Put {}'.format(id))
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
            well, created = network.well_set.update_or_create(name=id, defaults = {
                'location': coords,
                'description': remarks,
                'maaiveld': surface,
                'date': parse_date(date),
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
                depth /= 100.0 # kabellengte is in cm tov bovenkant buis
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
                          'user': request.user,
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
                            with fotos.open(name) as foto:
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
            

def import_handpeilingen(request, sheet='Handpeilingen'):
    ''' import manual measurements from excel sheet '''
    tz =pytz.timezone('Europe/Amsterdam')
    book = request.FILES['metadata']
    book.seek(0)
    df = pd.read_excel(book,sheet)
    for row in df.itertuples(index=False):
        if len(row) < 5:
            raise ValueError('Vijf kolommen verwacht: (put, filternummer, datum, tijd en waarde)')
        try:
            id,nr,date,time,level = row[0:5]
            level /= 100.0 # convert from centimeter to meter
            date = tz.localize(date + timedelta(hours=time.hour,minutes=time.minute,seconds=time.second))
            well = Well.objects.get(name=id)
            screen = well.screen_set.get(nr=nr)
            series_name = '%s HAND' % screen.mloc.name
            series,created = Handpeilingen.objects.get_or_create(screen=screen, defaults = {
                'name': series_name,
                'mlocatie':screen.mloc,
                'description':'Handpeiling', 
                'timezone':'Europe/Amsterdam', 
                'unit':'m NAP', 
                'type':'scatter', 
                'user':request.user,
                'refpnt': 'bkb'})
            if not created:
                if series.refpnt == 'nap':
                    # existing series wit different reference point. Convert level
                    if not screen.refpnt:
                        logger.error('Bovenkant filter onbekend')
                        continue
                    level = series.refpnt - level
            pt, created = series.datapoints.update_or_create(date=date,defaults={'value': level})
            if created:
                logger.info('Filter {}: handpeiling toegevoegd: ({}, {})'.format(screen, date, level))
            else:
                logger.info('Filter {}: handpeiling bijgewerkt: ({}, {})'.format(screen, date, level))
        except Well.DoesNotExist:
            logger.error('Well %s not found' % id)
        except Screen.DoesNotExist:
            logger.error('Screen %s/%03d not found' % (id, nr))
        
def handle_registration_files(request):

    # create dedicated log file
    folder = os.path.join(settings.LOGGING_ROOT, request.user.username)
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = 'import_{:%Y%m%d%H%M}.log'.format(datetime.now())
    logfile = os.path.join(folder, filename)
    logurl = settings.LOGGING_URL + request.user.username + '/' + filename
    handler = logging.FileHandler(logfile,'w')
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.addHandler(handler)

    import_metadata(request)
    import_handpeilingen(request)
        
    return logurl
