'''
#TNO_NITG_EXCHANGE_FILE=
#VERSION= 1, 1, 0
#FILE_SOURCE= Waterleidingmaatschappij Zuid-Brabant
#FILE_DATE= 29/08/2000
#DATA_SET_NAME_IN= DINO
#DATA_SET_NAME_OUT= DAWACO
#REMARK= Dit is een voorbeeld
#OBJECT_MEASUREMENT_TYPE= GWL
#COLUMN= 9
#COLUMN_INFO= 1, OBJECT_ID
#COLUMN_INFO= 2, OBJECT_SUB_ID
#COLUMN_INFO= 3, DATE, YYYY/MM/DD
#COLUMN_INFO= 4, TIME, HH24:MI:SS
#COLUMN_INFO= 5, VALUE, CM, MP
#COLUMN_INFO= 6, REM
#COLUMN_INFO= 7, QLT
#COLUMN_INFO= 8, REL
#COLUMN_INFO= 9, NOTE
#COLUMN_SEPERATOR= ;
#DATA_INSERT_METHOD=
#DATA_UPDATE_METHOD=
#EOH=
51EP0158;01;2000/05/14;12:55:00;77;;;;
51EP0158;01;1999/01/14;13:10:00;5;B;;;
51EP0158;01;1999/01/28;;1;;;;
51EP0158;01;1999/02/12;;;D;;;
B51E0159;003;2000/05/14;12:55:00;77;;;;
B51E0159;002;1999/01/14;13:10:00;5;B;;;
B51E0159;002;1999/01/28;;1;;;;
B51E015
9;002;1999/02/12;;;D;;;
'''
from datetime import datetime

'''
Created on Apr 24, 2017

@author: theo
'''

def write_header(f,source):
    f.write('#TNO_NITG_EXCHANGE_FILE=\n')
    f.write('#VERSION= 1, 1, 0\n')
    f.write('#FILE_SOURCE= %s\n' % source)
    f.write('#FILE_DATE= {:%Y/%m/%d}\n'.format(datetime.today()))
    f.write('#DATA_SET_NAME_IN= DINO\n')
    f.write('#DATA_SET_NAME_OUT= DIVER\n')
    f.write('#REMARK= Dit is een voorbeeld\n')
    f.write('#OBJECT_MEASUREMENT_TYPE= GWL\n')
    f.write('#COLUMN= 9\n')
    f.write('#COLUMN_INFO= 1, OBJECT_ID\n')
    f.write('#COLUMN_INFO= 2, OBJECT_SUB_ID\n')
    f.write('#COLUMN_INFO= 3, DATE, YYYY/MM/DD\n')
    f.write('#COLUMN_INFO= 4, TIME, HH24:MI:SS\n')
    f.write('#COLUMN_INFO= 5, VALUE, CM, MP\n')
    f.write('#COLUMN_INFO= 6, REM\n')
    f.write('#COLUMN_INFO= 7, QLT\n')
    f.write('#COLUMN_INFO= 8, REL\n')
    f.write('#COLUMN_INFO= 9, NOTE\n')
    f.write('#COLUMN_SEPERATOR= ;\n')
    f.write('#DATA_INSERT_METHOD=\n')
    f.write('#DATA_UPDATE_METHOD=\n')
    f.write('#EOH=\n')

def write_data(f,screen,**kwargs):
    series = screen.get_compensated_series(**kwargs)
    if series is None or screen.refpnt is None:
        return
    values = (screen.refpnt - series) * 100 # has to be in cm below measuring point
    well = screen.well
    for date,value in values.iteritems():
        f.write('{nitg};{filt:03d};{date:%Y/%m/%d};{time:%H:%M:%S};{value:.0f};;;;\n'.format(
            nitg = well.nitg,
            filt = screen.nr,
            date = date.date(),
            time = date.time(),
            value = value))

def export_well(f,well,**kwargs):
    write_header(f,kwargs.get('source','Acacia Water'))
    for s in well.screen_set.all():
        write_data(f, s)
