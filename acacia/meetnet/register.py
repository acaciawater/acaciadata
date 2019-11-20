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

logger = logging.getLogger('excel_import')

def handle_registration_files(request):
    import pandas as pd
    from django.contrib.gis.geos import Point
    from zipfile import ZipFile

    user = request.user
    network = Network.objects.first()
    
    metadata = request.FILES['metadata']
    df = pd.read_excel(metadata,'Putgegevens')

    archive = request.FILES.get('fotos')
    fotos = ZipFile(archive) if archive else None

    archive = request.FILES.get('boorstaten')
    logs = ZipFile(archive) if archive else None
    
    for _index, row in df.iterrows():
        id = str(row['ID'])
        x = row['X']
        y = row['Y']
        pobox = row['Postcode']
        street = row['Straat']
        housenumber= row['Huisnummer']
        town = row['Plaats']
        remarks = row['Opmerkingen locatie']
        date = as_date(row['Constructiedatum'])
        surface = row['Maaiveld']
        owner = row['Eigenaar']
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
                logger.info('Put {} aangemaakt'.format(id))
                register_well(well)
            else:
                logger.info('Put {} bijgewerkt'.format(id))
        except Exception as e:
            logger.exception(e)
            continue
        nr = row['Filternummer']
        refpnt = row['Bovenkant buis']
        top = row['Bovenkant filter m-MV']
        bottom = row['Onderkant filter m-MV']
        diameter = row['Diameter buis']
        material = row['Materiaal']
        screen, created = well.screen_set.update_or_create(nr=nr, defaults = {
            'refpnt': refpnt,
            'top': top,
            'bottom': bottom,
            'diameter': diameter,
            'material': material,
            })
        if created:
            logger.info('Filter {} aangemaakt'.format(screen))
            register_screen(screen)
        else:
            logger.info('Filter {} bijgewerkt'.format(screen))

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
            logger.info('Tijdreeks voor handpeilingen {} aangemaakt'.format(screen))
        else:
            logger.info('Tijdreeks voor handpeilingen {} bijgewerkt'.format(screen))

        serial = row['Logger ID']
        model = row['Logger type']
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
        if serial:
            datalogger, created = Datalogger.objects.get_or_create(serial=serial,defaults={'model':code})
            if created:
                logger.info('Logger {} aangemaakt'.format(serial))
        
            defaults = {
                'screen': screen,
                'start_date' : row.get('Datum installatie'),
                'refpnt': screen.refpnt,
                'depth': row['Kabellengte'],
                }
            pos, created = datalogger.loggerpos_set.update_or_create(logger=datalogger,defaults=defaults)
            if created:
                logger.info('Logger geinstallleerd op {}'.format(pos))

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
                
            if fotos:    
                for nr in range(1,6):
                    name = row['Foto %d'%nr]
                    if not pd.isna(name):
                        try:
                            with fotos.open(name,'r') as foto:
                                well.add_photo(name,foto)
                                logger.info('Foto toegevoegd: {}'.format(name))
                        except Exception as e:
                            logger.error('Kan foto niet toevoegen: {}'.format(e))
                    else:
                        break                            
 
            if logs:
                name = row['Boorstaat']
                if not pd.isna(name):
                    try:
                        with logs.open(name) as log:
                            well.set_log(name,log)
                            logger.info('Boorstaat toegevoegd: {}'.format(name))
                    except Exception as e:
                        logger.error('Kan boorstaat niet toevoegen: {}'.format(e))
            
    return df
