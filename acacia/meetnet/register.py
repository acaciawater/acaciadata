'''
Created on Nov 15, 2019

@author: theo
'''
from datetime import datetime, date, timedelta
import logging
import os
from zipfile import ZipFile

import dateutil
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
import pytz

from acacia.data.models import Generator
import acacia.meetnet.bro.models as bro
from acacia.meetnet.models import Network, Well, Datalogger, LoggerDatasource, DIVER_TYPES, Screen, \
    Handpeilingen
from acacia.meetnet.util import register_well, register_screen
import pandas as pd


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
    errors = 0
    
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

    # open excel file as pandas dataframe
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
        
        # get basic well data
        id = get('ID')
        if id:
            id=id.strip()
        if not id:
            continue
        logger.info('Put {}'.format(id))
        x = get('X',float)
        y = get('Y',float)
        pobox = get('Postcode')
        street = get('Straat')
        housenumber= get('Huisnummer')
        town = get('Plaats')
        remarks = get('Opmerkingen locatie')
        date = get('Constructiedatum')
        surface = get('Maaiveld',float)
        owner = get('Eigenaar')
        coords = Point(x,y,srid=28992)
        coords.transform(4326)
        try:
            # ceate or update well
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
            errors+=1
            continue

        # create or update BRO info
        try:
            gmw_data = {
                'user': request.user,
                'maintenanceResponsibleParty': get('Onderhoudende instantie'),
                'deliveryContext': get('Kader'),
                'constructionStandard': get('Kwaliteitsnorm'),
                'wellHeadProtector': get('Afwerking'),
            }
            try:
                well.bro.update(**gmw_data)
                well.bro.save()
                logger.info('BRO data voor put {} bijgewerkt'.format(well))
            except ObjectDoesNotExist:
                bro.GroundwaterMonitoringWell.create_for_well(well, **gmw_data)
                logger.info('BRO data voor put {} aangemaakt'.format(well))
        except Exception as e:
            logger.error('BRO data voor put {} niet aangemaakt/bijgewerkt: {}'.format(well,e))
            errors+=1
            
        nr = get('Filternummer',int) or 1
        refpnt = get('Bovenkant buis',float)
        top = get('Bovenkant filter m-MV',float)
        bottom = get('Onderkant filter m-MV',float)
        diameter = get('Diameter buis',float)
        material = get('Materiaal') or 'pvc'
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

        try:
            tube_data = {
                'user': request.user,
                'tubeType': get('Buistype'),
                'artesianWellCapPresent': get('Drukdop'),
                'sedimentSumpPresent': get('Zandvang'),
                'tubePackingMaterial': get('Omstorting'),
                'tubeStatus': get('Status'),
            }
            try:
                screen.bro.update(**tube_data)
                screen.bro.save()
                logger.info('BRO data voor filter {} bijgewerkt'.format(screen))
            except ObjectDoesNotExist:
                bro.MonitoringTube.create_for_screen(screen, **tube_data)
                logger.info('BRO data voor filter {} bijgewerkt'.format(screen))
        except Exception as e:
            logger.error('BRO data voor filter {} niet aangemaakt/bijgewerkt: {}'.format(screen,e))
            errors+=1

        if fotos:    
            for nr in range(1,6):
                name = get('Foto %d'%nr)
                if name:
                    try:
                        with fotos.open(name) as foto:
                            well.add_photo(name,foto,'png')
                            logger.info('Foto toegevoegd: {}'.format(name))
                    except Exception as e:
                        logger.error('Kan foto niet toevoegen: {}'.format(e))
                        errors+=1
                else:
                    break                            
        
        if logs:
            name = get('Boorstaat')
            if name:
                try:
                    with logs.open(name) as log:
                        well.set_log(name,log,'png')
                        logger.info('Boorstaat toegevoegd: {}'.format(name))
                except Exception as e:
                    logger.error('Kan boorstaat niet toevoegen: {}'.format(e))
                    errors+=1
            
        serial = get('Logger ID',None)
        if serial:
            if type(serial) == float:
                serial = str(int(serial))
            else:
                serial = str(serial)
            
            model = get('Logger type')
            if not model:
                logger.error('Logger type ontbreekt')
                errors+=1
                continue
            modelname = model.lower()

            # determine logger code from model name
            choice = filter(lambda x: x[1].lower() == modelname, DIVER_TYPES)
            if choice:
                code = choice[0][0]
            else:
                logger.error('Onbekend logger type: {}'.format(model))
                errors+=1
                continue

            # get/create datalogger
            datalogger, created = Datalogger.objects.get_or_create(serial=serial,defaults={'model':code})
            if created:
                logger.info('Logger {} aangemaakt'.format(serial))
        
            # install datalogger
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
                logger.info('Logger {} geinstallleerd in filter {}'.format(serial, str(screen)))
            else:
                logger.info('Metadata van logger {} in filter {} bijgewerkt'.format(serial, str(screen)))


            # defermine generator
            defaults = {'description': '{} datalogger {}'.format(model, serial),
                      'meetlocatie': screen.mloc,
                      'user': request.user,
                      }
            if modelname.startswith('elli'):
                generator_name = 'Ellitrack'
                defaults.update({
                    'url': settings.FTP_URL,
                    'username': settings.FTP_USERNAME,
                    'password': settings.FTP_PASSWORD,
                    'timezone': 'Europe/Amsterdam',
                    'config': '{{"logger": "{}"}}'.format(serial)
                })
            elif modelname.startswith('blik'):
                generator_name = 'Bliksensing'
                defaults.update({
                    'timezone': 'UTC',
                    'config': '{{"node": "{}"}}'.format(serial)
                })
            else:
                generator_name = 'Schlumberger'
                defaults.update({'timezone': 'Etc/GMT-1'})
                
            defaults.update({'generator':Generator.objects.get(name__iexact=generator_name)})

            # get/create datasource
            ds, created = LoggerDatasource.objects.update_or_create(
                logger = datalogger,
                name = serial,
                defaults = defaults)
            if created:
                ds.locations.add(screen.mloc)
                logger.info('Gegevensbron %s aangemaakt' % ds)
            else:
                logger.info('Gegevensbron %s bijgewerkt' % ds)

    return errors

def import_handpeilingen(request, sheet='Handpeilingen'):
    ''' import manual measurements from excel sheet '''
    tz =pytz.timezone('Europe/Amsterdam')
    errors = 0
    book = request.FILES['metadata']
    book.seek(0)
    df = pd.read_excel(book,sheet)
    for row in df.itertuples(index=False):
        if len(row) < 5:
            raise ValueError('Vijf kolommen verwacht: (put, filternummer, datum, tijd en waarde)')
        if any(pd.isna(value) for value in row[:5]):
            # value needed in all columns
            continue
        try:
            id,nr,date,time,level = row[:5]
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
                'unit':'m', 
                'type':'scatter', 
                'user':request.user,
                'refpnt': 'bkb'})
            if not created:
                if series.refpnt == 'nap':
                    # TODO: existing series with different reference point. Convert level
                    if not screen.refpnt:
                        logger.error('Bovenkant filter onbekend')
                        errors += 1
                        continue
                    level = screen.refpnt - level
            pt, created = series.datapoints.update_or_create(date=date,defaults={'value': level})
            if created:
                logger.info('Filter {}: handpeiling toegevoegd: ({}, {})'.format(str(screen), date, level))
            else:
                logger.info('Filter {}: handpeiling bijgewerkt: ({}, {})'.format(str(screen), date, level))
        except Well.DoesNotExist:
            logger.error('Well %s not found' % id)
            errors+=1
        except Screen.DoesNotExist:
            logger.error('Screen %s/%03d not found' % (id, nr))
            errors+=1

    return errors

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

    errors = import_metadata(request) + import_handpeilingen(request)
        
    return (errors, logurl)
