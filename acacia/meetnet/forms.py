'''
Created on Feb 11, 2015

@author: theo
'''
import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from acacia.meetnet.models import DIVER_TYPES, Screen, Datalogger
from datetime import date
from django.utils.timezone import now
from acacia.data.models import Datasource

class MultiFileInput(forms.FileInput):
    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return [files.get(name)]


class MultiFileField(forms.FileField):
    widget = MultiFileInput
    default_error_messages = {
        'min_num': _(u'Ensure at least %(min_num)s files are uploaded (received %(num_files)s).'),
        'max_num': _(u'Ensure at most %(max_num)s files are uploaded (received %(num_files)s).'),
        'file_size': _(u'File %(uploaded_file_name)s exceeded maximum upload size.'),
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            i = super(MultiFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret

    def validate(self, data):
        super(MultiFileField, self).validate(data)
        num_files = len(data)
        if len(data) and not data[0]:
            num_files = 0
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})
        for uploaded_file in data:
            if self.maximum_file_size and uploaded_file.size > self.maximum_file_size:
                raise ValidationError(self.error_messages['file_size'] % {'uploaded_file_name': uploaded_file.name})

class UploadFileForm(forms.Form):
    filename = MultiFileField(label='Selecteer MON bestand(en)')
    screen = forms.ModelChoiceField(queryset=Screen.objects.order_by('well__name','nr'), required=False)
    
def validate_serial(value):
    if Datalogger.objects.filter(serial=value).exists():
        raise ValidationError(
            _('A datalogger with serial number %(value)s already exists'),
            params={'value': value},
        )
    if Datasource.objects.filter(name=value).exists():
        raise ValidationError(
            _('A datasource with name %(value)s already exists'),
            params={'value': value},
        )

class AddLoggerForm(forms.Form):
    ''' Create a datalogger with installation '''
    model = forms.ChoiceField(label=_('loggermodel'), initial='etd2', choices=DIVER_TYPES)
    serial = forms.CharField(max_length=50, label=_('serialnumber'), validators=[validate_serial])
    screen = forms.ModelChoiceField(label=_('screen'), queryset=Screen.objects.all()) # or only screens without a logger installation?
    depth = forms.FloatField(label=_('installationdepth'))
    start = forms.DateTimeField()

    def clean_serial(self):
        model = self.cleaned_data['model']
        data = self.cleaned_data['serial']
        if model.startswith('etd'): # ellitrack
            pattern=r'^(?P<y>\d{2})(?P<m>\d{2})(?P<d>\d{2})(?P<nr>\d{2})$'
            match = re.match(pattern, data)
            if match:
                y = int(match.group('y'))
                m = int(match.group('m'))
                d = int(match.group('d'))
                try:
                    datum = date(2000+y,m,d)
                    if datum.year>=2016 and datum.year <= now().year:
                        return data
                except:
                    pass
        else:
            # Van Essen
            pattern=r'^\w{5}$'
            match = re.match(pattern, data)
            if match:
                return data
        raise forms.ValidationError(_('Invalid serial number'))
    
class UploadRegistrationForm(forms.Form):
    metadata = forms.FileField(label=_('Metadata'),required=True)
    fotos = forms.FileField(label=_('Fotos'),required=False)
    boorstaten = forms.FileField(label=_('Boorstaten'),required=False)
