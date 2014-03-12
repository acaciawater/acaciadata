'''
Created on Feb 28, 2014

@author: theo
'''
from django.utils.text import slugify
from acacia import settings

def project_upload(instance, filename):
    return '/'.join(['images',
                     slugify(instance.name), 
                     filename])

def locatie_upload(instance, filename):
    return '/'.join(['images',
                     slugify(instance.project.name), 
                     slugify(instance.name), 
                     filename])

def meetlocatie_upload(instance, filename):
    return '/'.join(['images',
                     slugify(instance.project.name), 
                     slugify(instance.projectlocatie.name), 
                     slugify(instance.name), 
                     filename])

def sourcefile_upload(instance, filename):
    sourcefile = instance
    datasource = sourcefile.datasource
    meetlocatie = datasource.meetlocatie
    projectlocatie = meetlocatie.projectlocatie
    project = projectlocatie.project
    return '/'.join([slugify(project.name), 
                     slugify(projectlocatie.name), 
                     slugify(meetlocatie.name), 
                     settings.UPLOAD_DATAFILES,
                     slugify(datasource.name), 
                     filename])

def param_thumb_upload(instance, filename):
    parameter = instance
    datasource = parameter.datasource
    meetlocatie = datasource.meetlocatie
    projectlocatie = meetlocatie.projectlocatie
    project = projectlocatie.project
    return '/'.join([
                     slugify(project.name),
                     slugify(projectlocatie.name),
                     slugify(meetlocatie.name),
                     settings.UPLOAD_THUMBNAILS, 
                     slugify(datasource.name),
                     'parameter', 
                     filename])

def series_thumb_upload(instance, filename):
    parameter = instance.parameter
    datasource = parameter.datasource
    meetlocatie = datasource.meetlocatie
    projectlocatie = meetlocatie.projectlocatie
    project = projectlocatie.project
    return '/'.join([slugify(project.name),
                     slugify(projectlocatie.name),
                     slugify(meetlocatie.name),
                     settings.UPLOAD_THUMBNAILS, 
                     slugify(datasource.name),
                     'series', 
                     filename])
