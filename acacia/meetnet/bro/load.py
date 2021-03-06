import os
from django.contrib.gis.utils import LayerMapping
from models import MapSheet

# Auto-generated `LayerMapping` dictionary for MapSheet model
mapping = {
    'area' : 'AREA',
    'perimeter' : 'PERIMETER',
    'topo_2561_field' : 'TOPO_2561_',
    'topo_25611' : 'TOPO_25611',
    'bladnaam' : 'BLADNAAM',
    'nr' : 'NR',
    'ltr' : 'LTR',
    'district' : 'DISTRICT',
    'blad' : 'BLAD',
    'geom' : 'POLYGON',
}

shapefile = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'fixtures', 'Kaartbladen.shp'),
)

def run(verbose=True):
    ''' load mapsheets from a shapefile '''
    lm = LayerMapping(MapSheet, shapefile, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)