from django.test import TestCase
from acacia.data.models import Project, Series
from django.contrib.gis.geos.point import Point
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import pytz
from acacia.meetnet.models import CompoundSeries

# Create your tests here.
class CompoundTest(TestCase):

    def createdb(self):
        admin = User.objects.create(username='admin',is_staff=True, is_superuser=True)
        project = Project.objects.create(name='test')
        ploc = project.projectlocatie_set.create(name='test',location=Point(4.5,52.5,srid=4326))
        mloc = ploc.meetlocatie_set.create(name='test',location=ploc.location)
        series1 = mloc.series_set.create(name='series1',user=admin)
        series2 = mloc.series_set.create(name='series2',user=admin)
        date = pytz.utc.localize(datetime.now())
        comp = CompoundSeries.objects.create(name='compound1',user=admin)
        for i in range(0,10):
            series1.datapoints.create(date=date,value=i)
            date = date + timedelta(hours=1)
        for i in range(10,20):
            series2.datapoints.create(date=date,value=i)
            date = date + timedelta(hours=1)
        for i in range(20,30):
            comp.datapoints.create(date=date,value=i)
            date = date + timedelta(hours=1)
        
        comp.add([series1,series2])
            
    def setUp(self):
        TestCase.setUp(self)
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.createdb()

    def tearDown(self):
        TestCase.tearDown(self)
                    
    def test1(self):
        series1 = Series.objects.get(name='series1')
        self.assertEqual(series1.datapoints.count(),10)
        series2 = Series.objects.get(name='series2')
        self.assertEqual(series2.datapoints.count(),10)
        
    def test_to_pandas(self):
        comp = CompoundSeries.objects.get(name='compound1')
        points = comp.to_pandas()
        p = points.iloc[23]
        self.assertEqual(p, 23)

    def test_properties(self):
        series1 = Series.objects.get(name='series1')
        series1.update_properties()
        self.assertEqual(series1.aantal(), 10)
        comp = CompoundSeries.objects.get(name='compound1')
        comp.update_properties()
        self.assertEqual(comp.aantal(), 30)
        self.assertEqual(comp.maximum(), 29)
        self.assertEqual(comp.eerste().value, 0)
        self.assertEqual(comp.laatste().value, 29)

    def test_overlap(self):
        admin = User.objects.first()
        series1 = Series.objects.get(name='series1')
        series2 = Series.objects.get(name='series2')
        comp = CompoundSeries.objects.create(name='compound2',user=admin)
        comp.add([series1, series2, series1])
        self.assertEqual(comp.aantal(), 20)
        
