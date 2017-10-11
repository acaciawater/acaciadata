from django.db import models
import requests

class AHN(models.Model):
    name = models.CharField(max_length=50)
    layer = models.CharField(max_length=50)
    resolution = models.FloatField()
    url = models.URLField()
    
    def __unicode__(self):
        return self.name

    def get_elevation(self, x, y):
        ''' gets elevation from AHN web service
        :param x: x-coordinate (EPSG:28992)
        :param y: y-coordinate (EPS:28992)
        :return: elevation in m +NAP
        :rtype: float
        '''  

        # define bounding box of 3x3 pixels
        box = (x-self.resolution,y-self.resolution,x+self.resolution,y+self.resolution)
        bbox = ','.join([str(x) for x in box])
        query = {'service': 'wms',
                 'version': '1.1.1', 
                 'request': 'getFeatureInfo', 
                 'layers': self.layer, 
                 'query_layers': self.layer,
                 'bbox': bbox, 
                 'width': 3, 
                 'height': 3, 
                 'format': 'img/png', 
                 'info_format': 'application/json',
                 'srs': 'EPSG:28992',
                 'x': 1,
                 'y': 1}
        response = requests.get(url=self.url, params=query)
        if response.ok:
            obj = response.json()
            features = obj['features']
            for f in features:
                props = f['properties']
                z = props['GRAY_INDEX']
                if z > 1e30 or z < -32767:
                    z = None
                return z
            raise Exception(response.reason)
        