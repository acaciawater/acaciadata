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
                     slugify(instance.project().name), 
                     slugify(instance.projectlocatie.name), 
                     slugify(instance.name), 
                     filename])

def sourcefile_upload(instance, filename):
    try:
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
    except:
        return '/'.join([settings.UPLOAD_DATAFILES, 'files', str(instance.pk), filename])
        
def param_thumb_upload(instance, filename):
    try:
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
    except:
        return '/'.join([settings.UPLOAD_THUMBNAILS, 'parameter', str(instance.pk), filename])
        
def series_thumb_upload(instance, filename):
    try:
        datasource = instance.datasource()
        meetlocatie = instance.meetlocatie()
        projectlocatie = instance.projectlocatie()
        project = instance.project()
        return '/'.join([slugify(project.name),
                     slugify(projectlocatie.name),
                     slugify(meetlocatie.name),
                     settings.UPLOAD_THUMBNAILS, 
                     slugify(datasource.name),
                     'series', 
                     filename])
    except:
        return '/'.join([settings.UPLOAD_THUMBNAILS, 'series', str(instance.pk), filename])
        