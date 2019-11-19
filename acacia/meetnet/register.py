'''
Created on Nov 15, 2019

@author: theo
'''
#ID    Bronhouder    Onderhoud    Kader    Kwaliteitsnorm    X    Y    Postcode    Straat    Huisnummer    Plaats    Opmerkingen locatie    Constructiedatum    Buistype    Diepte    Diameter buis    Materiaal    Afwerking    Drukdop    Zandvang    Omstorting    Status    Maaiveld    Bovenkant buis    Afstand MV-BKPB    Onderkant filter m-MV    Bovenkant filter m-MV    Onderkant filter m+NAP    Bovenkant filter m+NAP    Logger ID    Logger type    Kabellengte    Datum installatie    Boorstaat    Locatiefoto    Foto 2    Foto 3    Foto 4    Foto 5    Foto 6
import logging

from django.conf import settings

from acacia.data.models import Generator
from acacia.meetnet.models import Network, Well, Handpeilingen, \
    Datalogger, LoggerDatasource
from acacia.meetnet.util import register_well, register_screen


logger = logging.getLogger(__name__)

def handle_registration_files(request):
    import pandas as pd
    from django.contrib.gis.geos import Point
    from zipfile import ZipFile

    metadata = request.FILES['metadata']
    user = request.user
    network = Network.objects.first()
    
    df = pd.read_excel(metadata,'Putgegevens')
    for _index, row in df.iterrows():
        id = row['ID']
        x = row['X']
        y = row['Y']
        pobox = row['Postcode']
        street = row['Straat']
        housenumber= row['Huisnummer']
        town = row['Plaats']
        remarks = row['Opmerkingen locatie']
        date = row['Constructiedatum']
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
        except:
            pass
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
        # TODO: determine generator from logger type
        generator = Generator.objects.get(name='Ellitrack')

        if serial:
            datalogger, created = Datalogger.objects.get_or_create(serial=serial,defaults={'model':model})
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
                defaults={'description': 'Ellitrack datalogger {}'.format(serial),
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
                
            # TODO: open photo archive only once    
            fotos = request.FILES['fotos']
            with ZipFile.open(fotos) as archive:
                for nr in range(1,6):
                    name = row['Foto %d'%nr]
                    if name:
                        with archive.open(name) as foto:
                            well.add_photo(name,foto)
                    else:
                        break                            
 
            # TODO: open well log archive only once    
            boorstaten = request.FILES['boorstaten']
            with ZipFile.open(boorstaten) as archive:
                name = row['Boorstaat']
                if name:
                    with archive.open(name) as log:
                        well.set_log(name,log)
                                 
            
    return df
