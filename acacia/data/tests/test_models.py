# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime

from django.test import TestCase
from django.contrib.gis.geos.point import Point
from django.contrib.auth.models import User

from acacia.data.models import Project, Generator, aware, Formula
from acacia.data.generators.generator import Generator as BaseGenerator
import acacia.data.actions as actions

testurl = u'http://localhost:8000/'

class MockGenerator(BaseGenerator):    
    def download(self, **kwargs):
        result = {'file.txt':unicode(dict(kwargs))}
        callback = kwargs.get('callback', None)
        if callback is not None:
            callback(result)
        return result
    
    def get_data(self, f, **kwargs):
        return pd.DataFrame(np.arange(24).reshape((6, 4)), index=pd.date_range('20170101', periods=6), columns=list('ABCD'))

    def get_parameters(self, fil):
        return {'A': {'description' : 'description', 'unit': 'unit'}, 'B': {'description' : 'description', 'unit': 'unit'}, 'C': {'description' : 'description', 'unit': 'unit'}, 'D': {'description' : 'description', 'unit': 'unit'}}


class ProjectModelTests(TestCase):
    def test_non_standard_unicode_name_is_retrievable(self):
        project = Project(name=u'ProjëctNaam')
        self.assertEqual(unicode(project), u'ProjëctNaam')
        
    def test_non_standard_unicode_name_through_database_is_retrievable(self):
        Project.objects.create(name=u'ProjëctNaam')
        project = Project.objects.get(name=u'ProjëctNaam')
        self.assertEqual(project.name, u'ProjëctNaam')
        
    def test_create_project_without_name_results_in_name_equal_to_empty_string(self):
        Project.objects.create()
        project = Project.objects.get(name=u'')
        self.assertEqual(project.name, u'')
        
    def test_it_is_possible_to_add_a_projectlocatie_to_a_project(self):
        project = Project.objects.create(name=u'ProjectNaam')
        self.assertEqual(project.location_count(), 0)
        project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        self.assertEqual(project.location_count(), 1)
        
    def test_projectlocatie_can_return_its_location_in_latlon_format(self):
        project = Project.objects.create(name=u'ProjectNaam')
        projectlocatie = project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        point = Point(x=157525,y=478043,srid=28992)
        point.transform(4326)
        self.assertEqual(projectlocatie.latlon().tuple, point.tuple)
        
    def test_it_is_possible_to_add_a_meetlocatie_to_a_projectlocatie(self):
        project = Project.objects.create(name=u'ProjectNaam')
        projectlocatie = project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        self.assertEqual(projectlocatie.location_count(), 0)
        projectlocatie.meetlocatie_set.create(name=u'MeetLocatie', location=Point(157520,478040))
        self.assertEqual(projectlocatie.location_count(), 1)
        
    def test_meetlocatie_can_return_its_location_in_latlon_format(self):
        project = Project.objects.create(name=u'ProjectNaam')
        projectlocatie = project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        meetlocatie = projectlocatie.meetlocatie_set.create(name=u'MeetLocatie', location=Point(157520,478040))
        point = Point(x=157520,y=478040,srid=28992)
        point.transform(4326)
        self.assertEqual(meetlocatie.latlon().tuple, point.tuple)
        
    def test_meetlocatie_can_access_its_project(self):
        project = Project.objects.create(name=u'ProjectNaam')
        projectlocatie = project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        meetlocatie = projectlocatie.meetlocatie_set.create(name=u'MeetLocatie', location=Point(157520,478040))
        self.assertEqual(meetlocatie.project(), project)
        
    def test_can_create_mock_generator(self):
        generator = Generator.objects.create(name=u'Generator', classname='acacia.data.tests.test_models.MockGenerator')
        generator_class = generator.get_class()
        gen = generator_class()
        self.assertEqual(gen.get_header(None),{})
        
    def test_it_is_possible_to_add_a_datasource_to_a_generator(self):
        generator = Generator.objects.create(name=u'Generator', classname='acacia.data.tests.test_models.MockGenerator')
        user = User.objects.create(username=u'UserName', password=u'PassWord')        
        self.assertEqual(generator.datasource_set.count(), 0)
        generator.datasource_set.create(name=u'DataSource', user=user)
        self.assertEqual(generator.datasource_set.count(), 1)
        
    def test_it_is_possible_to_add_a_datasource_to_a_meetlocatie_as_meetlocatie(self):
        project = Project.objects.create(name=u'ProjectNaam')
        projectlocatie = project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        meetlocatie = projectlocatie.meetlocatie_set.create(name=u'MeetLocatie', location=Point(157520,478040))
        generator = Generator.objects.create(name=u'Generator', classname='acacia.data.tests.test_models.MockGenerator')
        user = User.objects.create(username=u'UserName', password=u'PassWord')
        self.assertEqual(meetlocatie.datasource_set.count(), 0)
        generator.datasource_set.create(name=u'DataSource', user=user, meetlocatie=meetlocatie)
        self.assertEqual(meetlocatie.datasource_set.count(), 1)
        
    def test_it_is_possible_to_add_a_datasource_to_a_meetlocatie_as_locations(self):
        project = Project.objects.create(name=u'ProjectNaam')
        projectlocatie = project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        meetlocatie = projectlocatie.meetlocatie_set.create(name=u'MeetLocatie', location=Point(157520,478040))
        generator = Generator.objects.create(name=u'Generator', classname='acacia.data.tests.test_models.MockGenerator')
        user = User.objects.create(username=u'UserName', password=u'PassWord')
        self.assertEqual(meetlocatie.datasourcecount(), 0)
        datasource = generator.datasource_set.create(name=u'DataSource', user=user, meetlocatie=meetlocatie)
        self.assertEqual(meetlocatie.datasourcecount(), 0)
        self.assertEqual(datasource.locations.count(), 0) #Depending on the interpretation, this should be equal to 1 instead of 0.
        meetlocatie.datasources.add(datasource)
        self.assertEqual(meetlocatie.datasourcecount(), 1)
        self.assertEqual(datasource.locations.count(), 1)
        
        
        
    # From now on, use the following setup for every test.    
    # (project,projectlocatie,meetlocatie,generator,user,datasource) = self.setup_up_to_datasource()
    def setup_up_to_datasource(self):
        project = Project.objects.create(name=u'ProjectNaam')
        projectlocatie = project.projectlocatie_set.create(name=u'ProjectLocatie', location=Point(157525,478043))
        meetlocatie = projectlocatie.meetlocatie_set.create(name=u'MeetLocatie', location=Point(157520,478040))
        generator = Generator.objects.create(name=u'Generator', classname='acacia.data.tests.test_models.MockGenerator')
        user = User.objects.create(username=u'UserName', password=u'PassWord')
        datasource = generator.datasource_set.create(name=u'DataSource', user=user, meetlocatie=meetlocatie, url=testurl)
        meetlocatie.datasources.add(datasource)
        return (project,projectlocatie,meetlocatie,generator,user,datasource)
        
        
        
    def test_datasource_download_adds_a_sourcefile(self):
        (_,_,meetlocatie,_,_,datasource) = self.setup_up_to_datasource()
        self.assertEqual(datasource.sourcefiles.count(),0)
        datasource.download()
        self.assertEqual(datasource.sourcefiles.count(),1)
        self.assertEqual(meetlocatie.filecount(),1)
        
    def test_datasource_download_same_file_twice_adds_it_once_to_database(self):
        (_,_,_,_,_,datasource) = self.setup_up_to_datasource()
        datasource.download(start = datetime.datetime(1991,12,19))
        datasource.sourcefiles.filter(name='file.txt').update(name='file0.txt')
        datasource.download(start = datetime.datetime(1991,12,19))
        self.assertEqual(datasource.sourcefiles.count(),1)
        
    def test_datasource_download_different_file_results_in_two_files_in_database(self):
        (_,_,_,_,_,datasource) = self.setup_up_to_datasource()
        datasource.download(start = datetime.datetime(2017,01,01))
        datasource.sourcefiles.filter(name='file.txt').update(name='file0.txt')
        datasource.download(start = datetime.datetime(1991,12,19))
        self.assertEqual(datasource.sourcefiles.count(),2)
        
    def test_datasource_download_options(self):
        (_,_,_,_,_,datasource) = self.setup_up_to_datasource()
        datasource.config = '{"test1":0,"test2":"test3"}'
        datasource.download()
        file0 = datasource.sourcefiles.get(name='file.txt')
        next_start_string = str({'start':aware(file0.stop)})[1:-1]
        datasource.download()
        file1 = datasource.sourcefiles.get(name='file.txt')
        filecontent = file1.file.read()
        self.assertTrue("u'test1': 0" in filecontent)
        self.assertTrue("u'test2': u'test3'" in filecontent)
        self.assertTrue(next_start_string in filecontent)
        
    def test_datasource_update_parameters(self):
        (_,_,meetlocatie,_,_,datasource) = self.setup_up_to_datasource()
        datasource.download()
        self.assertEqual(datasource.parameter_set.count(),0)
        number_of_parameters = datasource.update_parameters()
        self.assertEqual(number_of_parameters,4)
        self.assertEqual(datasource.parameter_set.count(),4)
        self.assertEqual(meetlocatie.paramcount(),4)
        
    def test_datasource_get_data(self):
        (_,_,_,_,_,datasource) = self.setup_up_to_datasource()
        datasource.download()
        datasource.update_parameters()
        datasource.get_data()
        self.assertEqual(datasource.sourcefiles.get(name='file.txt').cols,4)
        
    def test_generate_datasource_series_creates_a_new_series(self):
        (_,_,meetlocatie,_,user,datasource) = self.setup_up_to_datasource()
        datasource.download()
        self.assertEqual(meetlocatie.series_set.count(),0)
        class RequestClass:
            def __init__(self, user):
                self.user = user
        modeladmin = None
        request = RequestClass(user)
        queryset = [datasource]
        actions.generate_datasource_series(modeladmin, request, queryset)
        self.assertEqual(meetlocatie.series_set.count(),4)
        
        
        
    # From now on, use the following setup for every test.    
    # (project,projectlocatie,meetlocatie,generator,user,datasource) = self.setup_up_to_generate_series()
    def setup_up_to_generate_series(self):
        (project,projectlocatie,meetlocatie,generator,user,datasource) = self.setup_up_to_datasource()
        datasource.download()
        class RequestClass:
            def __init__(self, user):
                self.user = user
        modeladmin = None
        request = RequestClass(user)
        queryset = [datasource]
        actions.generate_datasource_series(modeladmin, request, queryset)
        return (project,projectlocatie,meetlocatie,generator,user,datasource)
    
    
    
    
    
    
        # !!!!!!!!!! HIER GEBLEVEN !!!!!!!!!!!!!!!
    def test_series(self):
        (project,projectlocatie,meetlocatie,generator,user,datasource) = self.setup_up_to_generate_series()
        series = project.series()
        first_series = series[0];
        #print(first_series.to_pandas())
        self.assertEqual(first_series.maximum(),20.0)
        
    def test_berekende_reeks(self):
        (project,projectlocatie,meetlocatie,generator,user,datasource) = self.setup_up_to_generate_series()
        series_list = project.series()
        variabele1 = meetlocatie.variable_set.create(name="EersteReeks", series = series_list[0])
        variabele2 = meetlocatie.variable_set.create(name="TweedeReeks", series = series_list[1])
        berekende_reeks = Formula.objects.create(mlocatie=meetlocatie, name="Verschil", user=user)
        berekende_reeks.formula_variables.add(variabele1)
        berekende_reeks.formula_variables.add(variabele2)
        berekende_reeks.formula_text = "TweedeReeks-EersteReeks"
        berekende_reeks.save()
        #print(berekende_reeks.to_pandas()) #Gaat nog niet goed. Nu lege reeks. Reeks moet nog gemaakt worden.
        self.assertEqual(True,False)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    #def test_copy_example_setup(self):
    #    (project,projectlocatie,meetlocatie,generator,user,datasource) = self.setup_up_to_generate_series()
    #    self.assertEqual(True,True)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
