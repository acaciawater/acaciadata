'''
Created on Jun 3, 2014

@author: theo
'''
import logging
import matplotlib
from django.core.exceptions import MultipleObjectsReturned
matplotlib.use('agg')
import matplotlib.pylab as plt
from matplotlib import rcParams
from StringIO import StringIO
import math, pytz
import os,re
import datetime
import binascii
import numpy as np

from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from acacia.data.models import ProjectLocatie, Generator, DataPoint, MeetLocatie, SourceFile, Chart, Series
from acacia.data.generators import sws
from acacia.data.knmi.models import NeerslagStation, Station
from .models import Well, Screen, Datalogger, MonFile, Channel, LoggerDatasource

rcParams['font.family'] = 'sans-serif'
rcParams['font.size'] = '8'

logger = logging.getLogger(__name__)

# thumbnail size and resolution
THUMB_DPI=72
THUMB_SIZE=(9,3) # inch

def chart_for_screen(screen):
    plt.figure(figsize=THUMB_SIZE)
    plt.grid(linestyle='-', color='0.9')
    data = screen.get_levels('nap')
    n = len(data) / (THUMB_SIZE[0]*THUMB_DPI)
    if n > 1:
        #use data thinning: take very nth row
        data = data[::n]
    if len(data)>0:
        x,y = zip(*data)
        plt.plot_date(x, y, '-')
        y = [screen.well.maaiveld] * len(x)
        plt.plot_date(x, y, '-')

    hand = screen.get_hand('nap')
    if len(hand)>0:
        x,y = zip(*hand)
        plt.plot_date(x, y, 'ro',label='handpeiling')

    plt.title(screen)
    plt.ylabel('m tov NAP')
    img = StringIO() 
    plt.savefig(img,bbox_inches='tight', format='png')
    plt.close()    
    return img.getvalue()

def chart_for_well(well):
    fig=plt.figure(figsize=THUMB_SIZE)
    ax=fig.gca()
    plt.grid(linestyle='-', color='0.9')
    count = 0
    y = []
    x = []
    for screen in well.screen_set.all():
        data = screen.get_levels('nap')
        n = len(data) / (THUMB_SIZE[0]*THUMB_DPI)
        if n > 1:
            #use data thinning: take very nth row
            data = data[::n]
        if len(data)>0:
            x,y = zip(*data)
            plt.plot_date(x, y, '-', label=screen)
            count += 1

        hand = screen.get_hand('nap')
        if len(hand)>0:
            x,y = zip(*hand)
            plt.plot_date(x, y, 'ro', label='handpeiling')
            
    if len(x):
        y = [screen.well.maaiveld] * len(x)
        plt.plot_date(x, y, '-', label='maaiveld')

    plt.title(well)
    plt.ylabel('m tov NAP')
    if count > 0:
        leg=plt.legend()
        leg.get_frame().set_alpha(0.3)
    
    img = StringIO() 
    plt.savefig(img,format='png',bbox_inches='tight')
    plt.close()    
    return img.getvalue()

def encode_chart(chart):
    return 'data:image/png;base64,' + chart.encode('base64')

def make_chart(obj):
    if isinstance(obj,Well):
        return chart_for_well(obj)
    elif isinstance(obj,Screen):
        return chart_for_screen(obj)
    else:
        raise Exception('make_chart(): object must be a well or a screen')
    
def make_encoded_chart(obj):
    return encode_chart(make_chart(obj))

def recomp(screen,series,baros={},tz=pytz.FixedOffset(60)):
    ''' re-compensate timeseries for screen '''

    seriesdata = None
    for logpos in screen.loggerpos_set.all().order_by('start_date'):
        if logpos.refpnt is None:
            logger.warning('Referentiepunt ontbreekt voor {pos}'.format(pos=logpos))
            continue
        if logpos.depth is None:
            logger.warning('Inhangdiepte ontbreekt voor {pos}'.format(pos=logpos))
            continue
        if logpos.baro is None:
            logger.warning('Barometer ontbreekt voor {pos}'.format(pos=logpos))
            continue
        if seriesdata is None:
            meteo = logpos.baro
            logger.info('Compenseren voor luchtdrukreeks {}'.format(meteo))
        if logpos.baro in baros:
            baro = baros[logpos.baro]
        else:
            baro = logpos.baro.to_pandas()

            # if baro datasource = KNMI then convert from hPa to cm H2O
            dsbaro = logpos.baro.datasource()
            if dsbaro:
                gen = dsbaro.generator
                if 'knmi' in gen.name.lower() or 'knmi' in gen.classname.lower():
                    # TODO: use g at  baro location, not well location
                    baro = baro / (screen.well.g or 9.80638)
            
            baro = baro.tz_convert(tz)
            baros[logpos.baro] = baro
        for mon in logpos.monfile_set.all().order_by('start_date'):
            print ' ', logpos.logger, mon
            mondata = mon.get_data()
            if isinstance(mondata,dict):
                # Nov 2016: new signature for get_data 
                mondata = mondata.itervalues().next()
            data = mondata['PRESSURE']
            data = series.do_postprocess(data).tz_localize(tz)
            
            adata, abaro = data.align(baro)
            abaro = abaro.interpolate(method='time')
            abaro = abaro.reindex(data.index)
            data = data - abaro
            data.dropna(inplace=True)

            #clear datapoints with less than 10 cm of water
            data[data<10] = np.nan
            
            data = data / 100 + (logpos.refpnt - logpos.depth)
            if seriesdata is None:
                seriesdata = data
            else:
                seriesdata = seriesdata.append(data)
                
    if seriesdata is not None:
        seriesdata = seriesdata.groupby(level=0).last()
        seriesdata.sort(inplace=True)
        datapoints=[]
        for date,value in seriesdata.iteritems():
            value = float(value)
            if math.isnan(value) or date is None:
                continue
            datapoints.append(DataPoint(series=series, date=date, value=value))
        series.datapoints.all().delete()
        series.datapoints.bulk_create(datapoints)
        series.unit = 'm tov NAP'
        series.make_thumbnail()
        series.save()
    
def createmeteo(request, well):
    ''' Create datasources with meteo data for a well '''

    def docreate(name,closest,gen,start):
        instance = gen.get_class()()
        ploc, created = project.projectlocatie_set.get_or_create(name = name, defaults = {'description': name, 'location': closest.location})
        mloc, created = ploc.meetlocatie_set.get_or_create(name = name, defaults = {'description': name, 'location': closest.location})
        if created:
            logger.info('Meetlocatie {} aangemaakt'.format(name))   
        ds, created = mloc.datasources.get_or_create(name = name, defaults = {'description': name,'generator': gen, 'user': user, 'timezone': 'UTC',
                                                     'url': instance.url + '?stns={stn}&start={start}'.format(stn=closest.nummer,start=start)})
        if created:
            ds.download()
            ds.update_parameters()
            
            for p in ds.parameter_set.filter(name__in=candidates):
                try:
                    series, created = p.series_set.get_or_create(name = p.name, description = p.description, unit = p.unit, user = request.user)
                    series.replace()
                except Exception as e:
                    logger.error('ERROR creating series %s: %s' % (p.name, e))
    
    user = request.user

    candidates = ['PG', 'EV24', 'RD', 'RH', 'P', 'T']
    
    ploc = ProjectLocatie.objects.get(name=well.name)
    project = ploc.project
    
    gen = Generator.objects.get(classname__icontains='KNMI.meteo')
    closest = Station.closest(well.location)
    name = 'Meteostation {} (dagwaarden)'.format(closest.naam)
    docreate(name,closest,gen,'20140501')

    gen = Generator.objects.get(classname__icontains='KNMI.neerslag')
    closest = NeerslagStation.closest(well.location)
    name = 'Neerslagstation {}'.format(closest.naam)
    docreate(name,closest,gen,'20140501')

    gen = Generator.objects.get(classname__icontains='KNMI.uur')
    closest = Station.closest(well.location)
    name = 'Meteostation {} (uurwaarden)'.format(closest.naam)
    docreate(name,closest,gen,'2014050101')


logger = logging.getLogger('upload')

# l=logging.getLogger('acacia.data').addHandler(h)

def createmonfile(source, generator=sws.Diver()):
    ''' parse .mon file and create MonFile instance '''
    
    # default timeone for MON files = CET
    CET = pytz.timezone('CET')
    
    headerdict = generator.get_header(source)
    mon = MonFile()
    header = headerdict['HEADER']
    mon.company = header.get('COMPANY',None)
    mon.compstat = header.get('COMP.STATUS',None)
    if 'DATE' in header and 'TIME' in header:
        dt = header.get('DATE') + ' ' + header.get('TIME')
        mon.date = datetime.datetime.strptime(dt,'%d/%m/%Y %H:%M:%S').replace(tzinfo=CET)
    else:
        mon.date = datetime.datetime.now(CET)
    mon.monfilename = header.get('FILENAME',None)
    mon.createdby = header.get('CREATED BY',None)
    mon.num_points = int(header.get('Number of points','0'))
    
    s = headerdict['Logger settings']
    instype = s.get('Instrument type',None)
    parts = instype.split('=')
    mon.instrument_type = parts[-1] 
    mon.status = s.get('Status',None)
    serial = s.get('Serial number',None)
    if serial is not None:
        serial = re.split(r'[-\s+]',serial)[1]
    mon.serial_number = serial
    mon.instrument_number = s.get('Instrument number',None)
    mon.location = s.get('Location',None)
    mon.sample_period = s.get('Sample period',None)
    mon.sample_method = s.get('Sample method','T')
    mon.num_channels = int(s.get('Number of channels','1'))

    s = headerdict['Series settings']
    mon.start_date = datetime.datetime.strptime(s['Start date / time'],'%S:%M:%H %d/%m/%y').replace(tzinfo=CET)    
    mon.end_date = datetime.datetime.strptime(s['End date / time'], '%S:%M:%H %d/%m/%y').replace(tzinfo=CET)    

    channels = []
    for i in range(mon.num_channels):
        channel = Channel(number = i+1)
        name = 'Channel %d' % (i+1)
        s = headerdict[name]
        channel.identification = s.get('Identification',name)
        t = s.get('Reference level','0 -')
        channel.reference_level, channel.reference_unit = re.split(r'\s+',t)
        channel.range, channel.range_unit = re.split(r'\s+', s.get('Range','0 -'))
        channel.range_unit = repr(channel.range_unit)
        channel.reference_unit = repr(channel.reference_unit)
        channels.append(channel)
    return (mon, channels)

def addmonfile(request,network,f):
    ''' add monfile to database and create related tables '''
    filename = f.name    
    basename = os.path.basename(filename)
    logger.info('Verwerken van bestand ' + basename)
    error = (None,None)
    user = request.user
    generator = Generator.objects.get(name='Schlumberger')
    if not filename.lower().endswith('.mon'):
        logger.warning('Bestand {name} wordt overgeslagen: bestandsnaam eindigt niet op .MON'.format(name=basename))
        return error
    mon, channels = createmonfile(f)
    serial = mon.serial_number
    put = mon.location
    logger.info('Informatie uit MON file: Put={put}, diver={ser}'.format(put=put,ser=serial))
    
    datalogger, created = Datalogger.objects.get_or_create(serial=serial,defaults={'model': mon.instrument_type})
    if created:
        logger.info('Nieuwe datalogger toegevoegd met serienummer {ser}'.format(ser=serial))
    
    try:
        # find logger datasource by well/screen combination
        well = network.well_set.get(name=put)
        # TODO: find out screen number
        filter = 1
        screen = well.screen_set.get(nr=filter)

        # get installation depth from last existing logger
        existing_loggers = screen.loggerpos_set.all().order_by('start_date')
        last = existing_loggers.last()
        depth = last.depth if last else None
        
        pos, created = datalogger.loggerpos_set.get_or_create(screen=screen,refpnt=screen.refpnt,defaults={'baro': well.baro, 'depth': depth, 'start_date': mon.start_date, 'end_date': mon.end_date})
        if created:
            logger.info('Datalogger {log} gekoppeld aan filter {loc}'.format(log=serial,loc=unicode(screen)))
            if depth is None:
                logger.warning('Geen kabellengte beschikbaar voor deze logger')
            else:
                logger.warning('Kabellengte {} overgenomen van bestaande installatie'.format(depth))
        else:
            logger.info('Geinstalleerde logger {log} gevonden in filter {loc}'.format(log=serial,loc=unicode(screen)))

            # update dates of loggerpos
            shouldsave = False
            if not pos.end_date or pos.end_date < mon.end_date:
                pos.end_date = mon.end_date
                shouldsave = True
            if not pos.start_date or pos.start_date > mon.start_date:
                pos.start_date = mon.start_date
                shouldsave = True
            if shouldsave:
                pos.save()

        try:
            loc = MeetLocatie.objects.get(name=unicode(screen))
        except MeetLocatie.DoesNotExist:
            loc = MeetLocatie.objects.get(name='%s/%s' % (put,filter))

        # get/create datasource for logger
        ds, created = LoggerDatasource.objects.get_or_create(name=datalogger.serial,meetlocatie=loc,
                                                                 defaults = {'logger': datalogger, 'generator': generator, 'user': user, 'timezone': 'CET'})
    except Well.DoesNotExist:
        # this maybe a baro logger, not installed in a well
        try:
            well = None
            screen = None
            ds = LoggerDatasource.objects.get(logger=datalogger)
            loc = ds.meetlocatie
            pos = None
        except LoggerDatasource.DoesNotExist:
            logger.error('Gegevensbron/meetlocatie voor datalogger ontbreekt')
            return error
        except MultipleObjectsReturned:
            logger.error('Meerdere gegevensbronnen voor deze datalogger')
            return error
    except Screen.DoesNotExist:
        logger.error('Filter {filt} niet gevonden voor put {put}'.format(put=put, filt=filter))
        return error

    f.seek(0)
    contents = f.read()
    mon.crc = abs(binascii.crc32(contents))
    try:
        sf = ds.sourcefiles.get(crc=mon.crc)
        logger.warning('Identiek bestand bestaat al in gegevensbron {ds}'.format(ds=unicode(ds)))
    except SourceFile.DoesNotExist:
        # add source file
        mon.name = mon.filename = basename
        mon.datasource = ds
        mon.source = pos
        mon.user = ds.user
        mon.file.save(name=filename, content=ContentFile(contents))
        mon.get_dimensions()
        mon.channel_set.add(*channels)
        mon.save()

        logger.info('Bestand {filename} toegevoegd aan gegevensbron {ds} voor logger {log}'.format(filename=basename, ds=unicode(ds), log=unicode(pos)))
        return (mon,screen)
    return error

def update_series(request,screen):
    user=request.user
    name = '%s COMP' % screen
    series, created = Series.objects.get_or_create(name=name,defaults={'user':user})
    try:
        meetlocatie = MeetLocatie.objects.get(name=unicode(screen))
        series.mlocatie = meetlocatie
        series.save()
    except:
        logger.exception('Meetlocatie niet gevonden voor filter {screen}'.format(screen=unicode(screen)))
        return

    recomp(screen, series)
                 
    #maak/update grafiek
    chart, created = Chart.objects.get_or_create(name=unicode(screen), defaults={
                'title': unicode(screen),
                'user': user, 
                'percount': 0, 
                })
    chart.series.get_or_create(series=series, defaults={'label' : 'm tov NAP'})

    # handpeilingen toevoegen (als beschikbaar)
    if hasattr(meetlocatie, 'manualseries_set'):
        name = '%s HAND' % screen
        for hand in meetlocatie.manualseries_set.filter(name=name):
            chart.series.get_or_create(series=hand,defaults={'type':'scatter', 'order': 2})
    
    make_chart(screen)

def handle_uploaded_files(request, network, localfiles):
    num = len(localfiles)
    if num == 0:
        return
    #incstall handler that buffers logrecords to be sent by email 
    buffer=logging.handlers.BufferingHandler(20000)
    logger.addHandler(buffer)
    try:
        logger.info('Verwerking van %d bestand(en)' % num)
        screens = set()
        wells = set()
        result = {}
        for pathname in localfiles:
            msg = []
            try:
                filename = os.path.basename(pathname)
                with open(pathname) as f:
                    mon,screen = addmonfile(request,network, f)
                if not mon:
                    msg.append('Niet gebruikt')
                    logger.warning('Bestand {name} overgeslagen'.format(name=filename))
                else:
                    msg.append('Succes')
                    if screen:
                        screens.add(screen)
                        wells.add(screen.well)
            except Exception as e:
                logger.exception('Probleem met bestand {name}: {error}'.format(name=filename,error=e))
                msg.append('Fout: '+unicode(e))
                continue
            result[filename] = ', '.join(msg)
    
        logger.info('Bijwerken van tijdreeksen')
        num = 0
        for s in screens:
            try:
                logger.info('Tijdreeks {}'.format(unicode(s)))
                update_series(request, s)
                num += 1
            except Exception as e:
                logger.exception('Bijwerken tijdreeksen voor filter {screen} mislukt: {error}'.format(screen=unicode(s), error=e))
        logger.info('{} tjdreeksen bijgewerkt'.format(num))

        logger.info('Bijwerken van grafieken voor putten')
        num=0
        for w in wells:
            try:
                logger.info('Put {}'.format(unicode(w)))
                make_chart(w)
                num += 1
            except Exception as e:
                logger.exception('Bijwerken van grafieken voor put {well} mislukt: {error}'.format(well=unicode(w), error=e))
        logger.info('{} grafieken bijgewerkt'.format(num))

        if request.user.email:
            
            logbuffer = buffer.buffer
            buffer.flush()

            logger.debug('Sending email to %s (%s)' % (request.user.get_full_name() or request.user.username, request.user.email))
            
            name=request.user.first_name or request.user.username
            html_message = render_to_string('notify_email_nl.html', {'name': name, 'network': network, 'result': result, 'logrecords': logbuffer})
            message = render_to_string('notify_email_nl.txt', {'name': name, 'network': network, 'result': result, 'logrecords': logbuffer})
            request.user.email_user(subject='Meetnet {net}: bestanden verwerkt'.format(net=network), message=message, html_message = html_message)
    finally:
        logger.removeHandler(buffer)
