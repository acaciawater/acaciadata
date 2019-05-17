'''
TITEL: FEWS Menyanthes Export
GEBRUIKERSNAAM: WielsmaEv
PERIODE: 2004/10/12-2004/12/31
DATUM:2016/12/27 11:10:01
REFERENTIE: NAP

LOCATIE,FILTERNUMMER,EXTERNE AANDUIDING,X COORDINAAT,Y COORDINAAT,MAAIVELD NAP,GESCHAT,MEETPUNT NAP,BOVENKANT FILTER,ONDERKANT FILTER,START DATUM,EINDE DATUM
28D0434,1,n/a,236263.71,484261.6,10.14,,10.8,5.0,7.0,2004/10/12,2004/12/31
28D0439,1,n/a,236924.24,484754.1,9.12,,9.02,6.0,7.01,2004/10/12,2004/12/31
28D0439,3,n/a,236924.24,484754.1,9.12,,9.02,30.0,32.0,2004/10/12,2004/12/31
28D0440,4,n/a,236457.45,483919.83,9.9,,9.74,33.0,35.0,2004/10/12,2004/12/31
28D0445,1,n/a,236485.47,482972.2,9.12,,9.07,2.0,4.0,2004/10/12,2004/12/31
28D0445,3,n/a,236485.47,482972.2,9.12,,9.0,23.0,25.0,2004/10/12,2004/12/31
28D0446,1,n/a,236183.87,484500.67,10.42,,10.37,8.02,10.02,2004/10/12,2004/12/31
28D0451,1,n/a,236278.49,484228.81,10.09,,10.64,5.0,7.0,2004/10/12,2004/12/31
28D0452,1,n/a,236325.89,484128.44,10.3,,10.8,3.5,4.5,2004/10/12,2004/12/31
28D0452,4,n/a,236325.89,484128.44,10.3,,10.74,30.0,32.0,2004/10/12,2004/12/31
28D0453,1,n/a,236424.24,484020.31,9.84,,10.42,1.0,2.0,2004/10/12,2004/12/31
28D0453,5,n/a,236424.24,484020.31,9.84,,10.32,30.0,32.0,2004/10/12,2004/12/31
28D0454,1,n/a,236620.45,483969.84,10.05,,10.58,2.0,3.0,2004/10/12,2004/12/31
28D0455,1,n/a,236972.75,483892.19,10.0,,9.97,5.5,7.5,2004/10/12,2004/12/31
28D0455,3,n/a,236972.75,483892.19,10.0,,9.94,30.0,32.0,2004/10/12,2004/12/31
28D0456,1,n/a,236370.65,484458.81,10.94,,11.44,8.4,10.4,2004/10/12,2004/12/31
28D0466,1,n/a,236056.58,484346.19,11.06,,11.55,8.0,10.0,2004/10/12,2004/12/31

LOCATIE,FILTERNUMMER,PEIL DATUM TIJD,STAND (NAP),BIJZONDERHEID
28D0434,1,2004/10/13 00:00:00,6.981,0
28D0434,1,2004/10/13 06:00:00,7.037,0
28D0434,1,2004/10/13 18:00:00,7.055,0
28D0434,1,2004/10/14 00:00:00,7.083,0
28D0434,1,2004/10/14 06:00:00,7.115,0
28D0434,1,2004/10/14 12:00:00,7.118,0
28D0434,1,2004/10/14 18:00:00,7.121,0
28D0434,1,2004/10/15 00:00:00,7.132,0
28D0434,1,2004/10/15 06:00:00,7.139,0
'''
from datetime import datetime
import pytz

def write_header(f):
    f.write("TITEL: FEWS Menyanthes Export\n")
    f.write("GEBRUIKERSNAAM: AcaciaWater\n")
    f.write("PERIODE: 2003/01/01-2018/12/31\n")
    f.write("DATUM: {}\n".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S")))
    f.write("REFERENTIE: NAP\n")

def write_meta(f,screens):
    f.write("\n")
    f.write("LOCATIE,FILTERNUMMER,EXTERNE AANDUIDING,X COORDINAAT,Y COORDINAAT,MAAIVELD NAP,GESCHAT,MEETPUNT NAP,BOVENKANT FILTER,ONDERKANT FILTER,START DATUM,EINDE DATUM\n")
    for screen in screens:
        if not screen.has_data():
            continue
        well = screen.well
        series= screen.find_series()
        loc = well.RD()
        mv = well.maaiveld or well.ahn or 0
        f.write(','.join(map(str,[
            well.nitg, 
            screen.nr, 
            well.name, 
            round(loc.x,2), 
            round(loc.y,2), 
            well.maaiveld, 
            well.ahn, 
            screen.refpnt, 
            mv-screen.top, 
            mv-screen.bottom, 
            series.van().strftime('%Y/%m/%d'), 
            series.tot().strftime('%Y/%m/%d')])))
        f.write("\n")
    
def write_data(f,screens,**kwargs):
    tz = pytz.timezone('Etc/GMT-1')
    f.write("\n")
    f.write("LOCATIE,FILTERNUMMER,PEIL DATUM TIJD,STAND (NAP),BIJZONDERHEID\n")
    for screen in screens:
        for p in screen.find_series().datapoints.order_by('date'):
            f.write('{nitg},{filt},{date:%Y/%m/%d %H:%M:%S},{value:.3f},\n'.format(
                nitg = screen.well.nitg,
                filt = screen.nr,
                date = p.date.astimezone(tz),
                value = p.value))

def export_screens(f,screens,**kwargs):
    write_header(f)
    write_meta(f, screens)
    write_data(f, screens)
