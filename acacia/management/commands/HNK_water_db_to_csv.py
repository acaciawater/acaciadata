# from django.contrib.gis.geos import Point
import csv
last_measurements = {}
from osgeo.osr import SpatialReference, CoordinateTransformation

def toWGS84(x,y):
    epsg28992 = SpatialReference()
    epsg28992.ImportFromEPSG(28992)
    epsg28992.SetTOWGS84(565.237,50.0087,465.658,-0.406857,0.350733,-1.87035,4.0812)
    epsg4326 = SpatialReference()
    epsg4326.ImportFromEPSG(4326)
    rd2latlon = CoordinateTransformation(epsg28992, epsg4326)
    latlon2rd = CoordinateTransformation(epsg4326, epsg28992)
    latlonz = rd2latlon.TransformPoint(x,y)
    return latlonz 

with open('hhnk_wrnm.txt', 'r') as f:
    lines = f.readlines()
for line in lines[1:]:
    l = line.split(';')
    if l[1] != '"SO4"':
        key = l[0]+';'+l[1]
        value = l[2]+';'+l[3]+';'+l[4]+';'+l[5]+';'+l[6]+';'+l[7]+';'+l[8]
        last_measurements[key]=value
        
# keys=last_measurements.keys()
# print keys[5],last_measurements[keys[5]]
      
location_reference = {}
with open('hhnk_meetpunt.txt', 'r') as f:
    lines = f.readlines()
for line in lines[1:]:
    l = line.split(';')
    key = l[0]
    if len(l) == 5:
        l[1] = l[1]+l[2]
        l.pop(2)
        l[1] = l[1].replace(';',':') 
    value= l[1:]
    location_reference[key] = value
    key = l[0]
    location_reference[key] = value
# "517073";"GELDHD";"Oppervlaktewater";"2014-07-22";"";396.000000;"mS/m";"niet van toepassing";""
# "001003";"Alkmaardermeer, circa 150 m. Noordelijk eilandje de Nes";112000.0;508000.0
     
waarnemer = ['Waarnemer']
meetpunt =['Meetpunt']
lats = ['Latitude']
longs = ['Longitude']
parameter = ['Parameter']
meeteenheden = ['Meeteenheid']
waarde = ['Waarde']
datum = ['Datum']
    
 
for key in last_measurements.keys():
    waarnemer.append('HNK-Water.nl')
    meetpunt.append(location_reference[key.split(';')[0]][0])
    y_rd = float(location_reference[key.split(';')[0]][1])
    x_rd = float(location_reference[key.split(';')[0]][2].replace('\r\n',''))
    coord = toWGS84(y_rd,x_rd)
    lat = coord[1]
    long = coord[0]
    lats.append(lat)
    longs.append(long)
    parameter.append(key.split(';')[1].replace('"',''))
    parameter
    meeteenheid = last_measurements[key].split(';')[4].replace('"','')
    datum.append(last_measurements[key].split(';')[1])
    if meeteenheid =='mS/m':
        meeteenheid = 'mS/cm'
        waarde.append(float(last_measurements[key].split(';')[3])/100)
    else:
        waarde.append(float(last_measurements[key].split(';')[3]))
    meeteenheden.append(meeteenheid)
    
with open('KRW_db_ec.csv', 'w') as ec:
    with open('KRW_db_cl.csv', 'w') as cl:
        writer_ec = csv.writer(ec, delimiter=';')
        writer_cl = csv.writer(cl, delimiter=';')
        for i in range(len(waarde)):
            l = [waarnemer[i],meetpunt[i],lats[i],longs[i],parameter[i],meeteenheden[i],waarde[i],datum[i]]
            if i == 0:
                writer_cl.writerow(l)
                writer_ec.writerow(l)
            elif parameter[i] == 'GELDHD':
                writer_ec.writerow(l)
            elif parameter[i] == 'Cl':
                writer_cl.writerow(l)
            
