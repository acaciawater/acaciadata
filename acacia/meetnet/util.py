'''
Created on Jun 3, 2014

@author: theo
'''
import logging
import matplotlib
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail.message import EmailMessage
from acacia.meetnet.models import MeteoData

matplotlib.use('agg')
import matplotlib.pylab as plt
from matplotlib import rcParams
from StringIO import StringIO
import math, pytz
import os,re
import datetime
import binascii
import numpy as np
import zipfile

from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings

from acacia.data.models import Project, Generator, DataPoint, MeetLocatie, SourceFile, Chart, Series,\
    Parameter
from acacia.data.generators import sws
from acacia.data.knmi.models import Station
from .models import Well, Screen, Datalogger, MonFile, Channel, LoggerDatasource

rcParams['font.family'] = 'sans-serif'
rcParams['font.size'] = '8'

logger = logging.getLogger(__name__)

# thumbnail size and resolution
THUMB_DPI=72
THUMB_SIZE=(12,5) # inch

def getcolor(index):
    colors = ['blue', 'red', 'green', 'black', 'orange', 'purple', 'brown', 'grey' ]
    index = index % len(colors) 
    return colors[index]

def screencolor(screen):
    return getcolor(screen.nr-1)

def chart_for_screen(screen,start=None,stop=None):
    fig=plt.figure(figsize=THUMB_SIZE)
    ax=fig.gca()

    datemin=start or datetime.datetime(2013,1,1)
    datemax=stop or datetime.datetime(2016,12,31)
    if start or stop:
        ax.set_xlim(datemin, datemax)

    plt.grid(linestyle='-', color='0.9')
    ncol = 0

    # sensor positie tov NAP berekenen en aan grafiek toevoegen
    if screen.refpnt is not None:
        depths = screen.loggerpos_set.filter(depth__isnull=False).order_by('start_date').values_list('start_date','end_date','depth')
        if len(depths)>0:
            data = []
            last = None
            for start,end,depth in depths:
                if last:
                    data.append((start,last))
                value = screen.refpnt - depth
                data.append((start,value))
                last = value
            data.append((end,last))    
            x,y = zip(*data)
            plt.plot_date(x,y,'--',label='diverpositie',color='orange')
            ncol += 1

    data = screen.get_levels('nap',rule='H')
#    n = len(data) / (THUMB_SIZE[0]*THUMB_DPI)
#     if n > 1:
#         #use data thinning: take very nth row
#         data = data[::n]
    if len(data)>0:
        x,y = zip(*data)
        plt.plot_date(x, y, '-', label='loggerdata',color='blue')
        ncol += 1

    # handpeilingen toevoegen
    hand = screen.get_hand('nap')
    if len(hand)>0:
        x,y = zip(*hand)
        plt.plot_date(x, y, 'o',label='handpeiling',color='red')
        ncol += 1
        
    # maaiveld toevoegen
    plt.axhline(y=screen.well.maaiveld, linestyle='--', label='maaiveld',color='green')
    ncol += 1

    plt.title(screen)
    plt.ylabel('m tov NAP')
    plt.legend(bbox_to_anchor=(0.5, -0.1), loc='upper center',ncol=ncol,frameon=False)
    
    img = StringIO() 
    plt.savefig(img,bbox_inches='tight', format='png')
    plt.close()    
    return img.getvalue()

def chart_for_well(well,start=None,stop=None):
    fig=plt.figure(figsize=THUMB_SIZE)
    ax=fig.gca()
    datemin=start or datetime.datetime(2013,1,1)
    datemax=stop or datetime.datetime(2016,12,31)
    if start or stop:
        ax.set_xlim(datemin, datemax)
    plt.grid(linestyle='-', color='0.9')
    ncol = 0
    index = 0
    for screen in well.screen_set.all():
        data = screen.get_levels('nap',rule='H')
#         n = len(data) / (THUMB_SIZE[0]*THUMB_DPI)
#         if n > 1:
#             #use data thinning: take very nth row
#             data = data[::n]
        if len(data)>0:
            x,y = zip(*data)
            color=getcolor(index)
            plt.plot_date(x, y, '-',label='filter {}'.format(screen.nr),color=color)
            ncol += 1

            hand = screen.get_hand('nap')
            if len(hand)>0:
                x,y = zip(*hand)
                if well.screen_set.count() == 1:
                    color = 'red'
                plt.plot_date(x, y, 'o', color=color)
                ncol += 1

            index += 1
            
    plt.ylabel('m tov NAP')

    plt.axhline(y=screen.well.maaiveld, linestyle='--', label='maaiveld',color='green')
    ncol += 1

    plt.legend(bbox_to_anchor=(0.5, -0.1), loc='upper center',ncol=min(ncol,5),frameon=False)
    plt.title(well)
    
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

    well = screen.well
    if not hasattr(well,'meteo') or well.meteo.baro is None:
        logger.error('Luchtdruk ontbreekt voor put {well}'.format(well=well))
        return
    baroseries = well.meteo.baro
    logger.info('Compenseren voor luchtdrukreeks {}'.format(baroseries))
    if baroseries in baros:
        baro = baros[baroseries]
    else:
        baro = baroseries.to_pandas()

        # if baro datasource = KNMI then convert from hPa to cm H2O
        dsbaro = baroseries.datasource()
        if dsbaro:
            gen = dsbaro.generator
            if 'knmi' in gen.name.lower() or 'knmi' in gen.classname.lower():
                # TODO: use g at  baro location, not well location
                baro = baro / (screen.well.g or 9.80638)
        
        baro = baro.tz_convert(tz)
        baros[baroseries] = baro
        
    seriesdata = None
    sumdry = 0
    for logpos in screen.loggerpos_set.all().order_by('start_date'):
        if logpos.refpnt is None:
            logger.warning('Referentiepunt ontbreekt voor {pos}'.format(pos=logpos))
            continue
        if logpos.depth is None:
            logger.warning('Inhangdiepte ontbreekt voor {pos}'.format(pos=logpos))
            continue

        # invalidate statistics
        logpos.clear_stats()
        
        for mon in logpos.monfile_set.all().order_by('start_date'):
            print ' ', logpos.logger, logpos.start_date, mon
            try:
                mondata = mon.get_data()
            except Exception as e:
                logger.error('Error reading {}: {}'.format(mon,e))
                continue
            if not mondata:
                logger.error('No data found in {}'.format(mon))
                continue

            if isinstance(mondata,dict):
                # Nov 2016: new signature for get_data 
                mondata = mondata.itervalues().next()

            data = mondata['PRESSURE']
            data = series.do_postprocess(data)
            
            # issue warning if data has points beyond timespan of barometer
            barostart = baro.index[0]
            dataend = data.index[0]
            if dataend < barostart:
                logger.warning('Geen luchtdruk gegevens beschikbaar voor {}'.format(barostart))
                continue
            baroend = baro.index[-1]
            datastart = data.index[0]
            if datastart > baroend:
                logger.warning('Geen luchtdruk gegevens beschikbaar na {}'.format(baroend))
                continue

            adata, abaro = data.align(baro)
            abaro = abaro.interpolate(method='time')
            abaro = abaro.reindex(data.index)
            abaro[:barostart] = np.NaN
            abaro[baroend:] = np.NaN
            data = data - abaro

            data.dropna(inplace=True)
            
            # clip logger data on timerange of baros data
            # data = data[max(barostart,datastart):min(baroend,dataend)]

            #clear datapoints with less than 5 cm of water
            data[data<5] = np.nan
            # count dry values
            dry = data.isnull().sum()
            if dry:
                logger.warning('Logger {}, MON file {}: {} out of {} measurements have less than 5 cm of water'.format(unicode(logpos),mon,dry,data.size))
            sumdry += dry
            
            data = data / 100 + (logpos.refpnt - logpos.depth)
            if seriesdata is None:
                seriesdata = data
            else:
                seriesdata = seriesdata.append(data)
                
    if seriesdata is not None:
        # remove duplicates
        seriesdata = seriesdata.groupby(seriesdata.index).last()
        # sort data
        seriesdata.sort_index(inplace=True)
#         if sumdry:
#             logger.warning('Screen {}: {} out of {} measurements have less than 5 cm of water'.format(unicode(screen),sumdry,seriesdata.size))
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
        
        series.validate(reset=True)

def drift_correct(series, manual):
    ''' correct drift with manual measurements (both are pandas series)'''
    # TODO: extrapolate series to manual 
    # calculate differences
    left,right=series.align(manual)
    # interpolate values on index of manual measurements
    left = left.interpolate(method='time')
    left = left.interpolate(method='nearest')
    # calculate difference at manual index
    diff = left.reindex(manual.index) - manual
    # interpolate differences to all measurements
    left,right=series.align(diff)
    right = right.interpolate(method='time')
    drift = right.reindex(series.index)
    drift = drift.fillna(0)
    return series-drift

def drift_correct_screen(screen,user):
    series = screen.get_compensated_series()
    manual = screen.get_manual_series()
    data = drift_correct(series,manual)
    name = unicode(screen) + 'CORR'
    cor, created = Series.objects.get_or_create(name=name,mlocatie=screen.mloc,defaults={'user':user})
    if created:
        cor.unit = 'm tov NAP'
    else:
        cor.datapoints.all().delete()
    datapoints=[]
    for date,value in data.iteritems():
        value = float(value)
        if math.isnan(value) or date is None:
            continue
        datapoints.append(DataPoint(series=cor, date=date, value=value))
    cor.datapoints.bulk_create(datapoints)
    cor.make_thumbnail()
    cor.save()
    
def register_well(well):
    # register well in acaciadata
    project,created = Project.objects.get_or_create(name=well.network.name)
    well.ploc, created = project.projectlocatie_set.get_or_create(name=well.name,defaults={'location': well.location})
    if created:
        well.save()

def register_screen(screen):
    # register screen in acaciadata
    project,created = Project.objects.get_or_create(name=screen.well.network.name)
    screen.well.ploc, created = project.projectlocatie_set.get_or_create(name=screen.well.name,defaults={'location': screen.well.location})
    if created:
        screen.well.save()
    screen.mloc, created = screen.well.ploc.meetlocatie_set.get_or_create(name=unicode(screen),defaults={'location': screen.well.location})
    screen.save()
        
def createmeteo(request, well):
    ''' Create datasources with meteo data for a well '''

    def docreate(name,closest,gen,start,candidates):
        instance = gen.get_class()()
        ploc, created = well.ploc.project.projectlocatie_set.get_or_create(name = name, defaults = {'description': name, 'location': closest.location})
        mloc, created = ploc.meetlocatie_set.get_or_create(name = name, defaults = {'description': name, 'location': closest.location})
        if created:
            logger.info('Meetlocatie {} aangemaakt'.format(name))   
        ds, created = mloc.datasources.get_or_create(name = name, defaults = {'description': name,'generator': gen, 'user': user, 'timezone': 'UTC',
                                                     'url': instance.url + '?stns={stn}&start={start}'.format(stn=closest.nummer,start=start)})
        if created:
            ds.download()
            ds.update_parameters()
            
        series_set = []
        for key in candidates:
            try:
                series = None
                p = ds.parameter_set.get(name=key)
                series, created = p.series_set.get_or_create(name = p.name, mloc = mloc, defaults = 
                        {'description': p.description, 'unit': p.unit, 'user': request.user})
                series.replace()
            except Parameter.DoesNotExist:
                logger.warning('Parameter %s not found in datasource %s' % (p.name, ds.name))
            except Exception as e:
                logger.error('ERROR creating series %s: %s' % (p.name, e))
            series_set.append(series)
        return series_set

    user = request.user

    #candidates = ['PG', 'EV24', 'RD', 'RH', 'P', 'T']
 
    if not hasattr(well,'meteo'):
        MeteoData.objects.create(well=well)

    meteo = well.meteo
    gen = Generator.objects.get(classname__icontains='KNMI.meteo')
    closest = Station.closest(well.location)
    name = 'Meteostation {} (dagwaarden)'.format(closest.naam)
    meteo.temperatuur,meteo.neerslag,meteo.verdamping = docreate(name,closest,gen,'20130101',['T','RH','EV24'])

#     gen = Generator.objects.get(classname__icontains='KNMI.neerslag')
#     closest3 = NeerslagStation.closest(well.location,3)
#     for closest in closest3:
#         name = 'Neerslagstation {}'.format(closest.naam)
#         docreate(name,closest,gen,'20130101',['RD'])

    gen = Generator.objects.get(classname__icontains='KNMI.uur')
    closest = Station.closest(well.location)
    name = 'Meteostation {} (uurwaarden)'.format(closest.naam)
    meteo.baro = docreate(name,closest,gen,'2013010101',['P'])

    meteo.save()
    
# l=logging.getLogger('acacia.data').addHandler(h)

def createmonfile(source, generator=sws.Diver()):
    ''' parse .mon file and create MonFile instance '''
    
    # default timeone for MON files = Etc/GMT-1
    CET = pytz.timezone('Etc/GMT-1')
    
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
    logger = logging.getLogger('upload')

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
    
    try:
        # find logger datasource by well/screen combination
        match = re.match(r'(\w+)[\.\-](\d{1,3}$)',put)
        if match:
            put = match.group(1)
            filter = int(match.group(2))
        else:
            filter = 1
        
        try:
            well = network.well_set.get(name__iexact=put)
        except Well.DoesNotExist:
            well = network.well_set.get(nitg__iexact=put)

        # TODO: find out screen number
        screen = well.screen_set.get(nr=filter)

        datalogger, created = Datalogger.objects.get_or_create(serial=serial,defaults={'model': mon.instrument_type})
        if created:
            logger.info('Nieuwe datalogger toegevoegd met serienummer {ser}'.format(ser=serial))
    
        # get installation depth from last existing logger
#         existing_loggers = screen.loggerpos_set.all().order_by('start_date')
#         last = existing_loggers.last()
#         depth = last.depth if last else None
        
        # get installation depth from previous logger
        prev = screen.loggerpos_set.filter(end_date__lte=mon.start_date)
        depth = prev.latest('end_date').depth if prev else None
            
        pos, created = datalogger.loggerpos_set.get_or_create(screen=screen,refpnt=screen.refpnt,start_date=mon.start_date, defaults={'depth': depth, 'end_date': mon.end_date})
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
            loc = MeetLocatie.objects.get(name='%s/%03d' % (well.nitg,filter))
        except MultipleObjectsReturned:
            logger.error('Meerdere meetlocaties gevonden voor dit filter')
            return error

        # get/create datasource for logger
        ds, created = LoggerDatasource.objects.get_or_create(name=datalogger.serial,meetlocatie=loc,
                                                                 defaults = {'logger': datalogger, 'generator': generator, 'user': user, 'timezone': 'Etc/GMT-1'})
    except Well.DoesNotExist:
        # this may be a baro logger, not installed in a well
        logger.error('Put niet gevonden: {}'.format(put))
        try:
            well = None
            screen = None
            ds = LoggerDatasource.objects.get(logger=Datalogger.objects.get(serial=serial))
            loc = ds.meetlocatie
            pos = None
        except (LoggerDatasource.DoesNotExist, Datalogger.DoesNotExist):
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

        logger.info('Bestand {filename} toegevoegd aan gegevensbron {ds} voor logger {log}'.format(filename=basename, ds=unicode(ds), log=unicode(pos or serial)))
        return (mon,screen)
    return error

def update_series(request,screen):

    user=request.user
    
    series = None
    for s in screen.mloc.series():
        if s.name.endswith('COMP') or s.name.startswith('Waterstand'):
            series = s
            break
    
    if series is None:
        # Make sure screen has been registered
        register_screen(screen)
        name = '%s COMP' % screen
        series, created = Series.objects.get_or_create(name=name,mlocatie=screen.mloc,defaults={'user':user})

    recomp(screen, series)
                 
    #maak/update grafiek
    chart, created = Chart.objects.get_or_create(name=unicode(screen), defaults={
                'title': unicode(screen),
                'user': user, 
                'percount': 0, 
                })
    chart.series.get_or_create(series=series, defaults={'label' : 'm tov NAP'})

    # handpeilingen toevoegen (als beschikbaar)
    if hasattr(screen.mloc, 'manualseries_set'):
        for hand in screen.mloc.manualseries_set.all():
            chart.series.get_or_create(series=hand,defaults={'type':'scatter', 'order': 2})
    
    make_chart(screen)

   
def handle_uploaded_files(request, network, localfiles):
    
    num = len(localfiles)
    if num == 0:
        return

    def process_file(f, name):
        mon,screen = addmonfile(request,network, f)
        if not mon or not screen:
            logger.warning('Bestand {name} overgeslagen'.format(name=name))
            return False
        else:
            screens.add(screen)
            wells.add(screen.well)
            return True
    
    def process_zipfile(pathname):
        z = zipfile.ZipFile(pathname,'r')
        result = {}
        for name in z.namelist():
            if name.lower().endswith('.mon'):
                bytes = z.read(name)
                io = StringIO(bytes)
                io.name = name
                result[name] = 'Success' if process_file(io, name) else 'Niet gebruikt'
        return result

    def process_plainfile(pathname):
        with open(pathname) as f:
            return 'Success' if process_file(f, os.path.basename(pathname)) else 'Niet gebruikt'
        
    #incstall handler that buffers logrecords to be sent by email 
    buffer=logging.handlers.BufferingHandler(20000)
    logger.addHandler(buffer)
    try:
        logger.info('Verwerking van %d bestand(en)' % num)
        screens = set()
        wells = set()
        result = {}
        for pathname in localfiles:
            filename = os.path.basename(pathname)
            try:
                if zipfile.is_zipfile(pathname): 
                    msg = process_zipfile(pathname)
                    result.update(msg) 
                    #result.update({filename+'-'+key: val for key,val in msg.iteritems()}) 
                else:
                    result[filename] = process_plainfile(pathname)
            except Exception as e:
                logger.exception('Probleem met bestand {name}: {error}'.format(name=filename,error=e))
                msg.append('Fout: '+unicode(e))
                continue
            
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
            msg = EmailMessage(subject='Meetnet {net}: bestanden verwerkt'.format(net=network), 
                                   body=message, 
                                   from_email=settings.DEFAULT_FROM_EMAIL, 
                                   to=[request.user.email],
                                   attachments=[('report.html',html_message,'text/html')])
            msg.send()
    finally:
        logger.removeHandler(buffer)
