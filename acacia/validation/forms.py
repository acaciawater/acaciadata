'''
Created on Nov 29, 2016

@author: theo
'''
from django import forms
from django.forms.fields import FileField

class UploadFileForm(forms.Form):
    filename = FileField(label='Selecteer Excel bestand(en)')

class ValidationForm(forms.Form):
    filename = FileField(label='Selecteer Excel bestand(en)')
