import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from acacia.meetnet.models import DIVER_TYPES, Screen, Datalogger, LoggerPos
from datetime import date
from django.utils.timezone import now
from acacia.data.models import Datasource
from acacia.meetnet.util import to_datetime


def validate_serial(value):
    if Datalogger.objects.filter(serial=value).exists():
        raise ValidationError(
            _('A sensor with serial number %(value)s already exists'),
            params={'value': value},
        )
    if Datasource.objects.filter(name=value).exists():
        raise ValidationError(
            _('A datasource with name %(value)s already exists'),
            params={'value': value},
        )


class LoggerAdminForm(forms.Form):
    screen = forms.ModelChoiceField(Screen.objects.all(), label=_('screen'))
    depth = forms.FloatField(label=_('cable length'), required=True)
    refpnt = forms.FloatField(label=_('reference point'), required=False)
    start_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'type': 'time', 'min':'00:00:00', 'max':'23:59:59'}))

    def clean_refpnt(self):
        refpnt = self.cleaned_data['refpnt']
        if refpnt is None:
            screen = self.cleaned_data['screen']
            refpnt = screen.refpnt
        return refpnt


class LoggerMoveForm(LoggerAdminForm):
    ''' Move a sensor '''
    logger = forms.ModelChoiceField(Datalogger.objects.all(), label=_('existing logger'))
    cur_screen = forms.ModelChoiceField(Screen.objects.all(), label=_('screen'), required=False)
    cur_depth = forms.FloatField(label=_('cable length'), required=False)
    cur_refpnt = forms.FloatField(label=_('reference point'), required=False)
    stop_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    stop_time = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'type': 'time', 'min':'00:00:00', 'max':'23:59:59'}))


class LoggerStopForm(forms.Form):
    ''' Stop a running sensor '''
    logger = forms.ModelChoiceField(Datalogger.objects.all(), label=_('logger'))
    stop_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    stop_time = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'type': 'time', 'min':'00:00:00', 'max':'23:59:59'}))

    def __init__(self, *args, **kwargs):
        super(LoggerStopForm, self).__init__(*args, **kwargs)
        self.fields['logger'].queryset = Datalogger.objects.filter(loggerpos__end_date__isnull=True)

    def clean_stop_time(self):
        data = super(LoggerStopForm, self).clean()
        stop = to_datetime(data['stop_date'], data['stop_time'])
        logger = data['logger']
        # check if stop is after current start_date of latest installation
        try:
            install = logger.loggerpos_set.filter(end_date__isnull=True).latest('start_date')
            if install.start_date > stop:
                raise ValidationError(
                    _('Stop date should be after latest installation date of logger: %(date)s'),
                    params={'date': install.start_date}
                    )
                
        except LoggerPos.DoesNotExist:
                raise ValidationError(
                    _('Logger is not running on %(stop)s'),
                    params={'stop': stop}
                    )
        return data['stop_time']

        
class LoggerStartForm(forms.Form):
    ''' Start a stopped sensor '''
    logger = forms.ModelChoiceField(Datalogger.objects.all(), label=_('logger'))
    start_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'type': 'time', 'min':'00:00:00', 'max':'23:59:59'}))

    def __init__(self, *args, **kwargs):
        super(LoggerStartForm, self).__init__(*args, **kwargs)
        self.fields['logger'].queryset = Datalogger.objects.filter(loggerpos__end_date__isnull=False)

    def clean_start_time(self):
        data = super(LoggerStartForm, self).clean()
        start = to_datetime(data['start_date'], data['start_time'])
        logger = data['logger']
        # check if start is after current start_date of latest installation
        try:
            install = logger.loggerpos_set.filter(end_date__isnull=False).latest('start_date')
            if install.start_date > start:
                raise ValidationError(
                    _('Starting date should be on or after latest installation date of logger: %(date)s'),
                    params={'date': install.start_date}
                    )
                
        except LoggerPos.DoesNotExist:
                raise ValidationError(
                    _('Logger is already running on %(start)s'),
                    params={'start': start}
                    )
        return data['start_time']


class LoggerRefreshForm(forms.Form):
    ''' 
    Refresh logger datafiles
    '''
    logger = forms.ModelChoiceField(Datalogger.objects.all(), label=_('logger'), required=True)
    start_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=True)
    stop_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)


class LoggerAddForm(LoggerAdminForm):
    ''' Create a sensor with installation '''
    model = forms.ChoiceField(label=_('loggermodel'), initial='etd2', choices=DIVER_TYPES)
    serial = forms.CharField(max_length=50, label=_('serialnumber'), validators=[validate_serial])

    def clean_serial(self):
        model = self.cleaned_data['model']
        data = self.cleaned_data['serial']
        if model.startswith('etd'):  # ellitrack
            pattern = r'^(?P<y>\d{2})(?P<m>\d{2})(?P<d>\d{2})(?P<nr>\d{2})$'
            match = re.match(pattern, data)
            if match:
                y = int(match.group('y'))
                m = int(match.group('m'))
                d = int(match.group('d'))
                try:
                    datum = date(2000 + y, m, d)
                    if datum.year >= 2016 and datum.year <= now().year:
                        return data
                except:
                    pass
        elif model.starts_with('blik'):
            pattern = r'^\d+$'
            match = re.match(pattern, data)
            if match:
                return data
        else:
            # Van Essen
            pattern = r'^\w{5}$'
            match = re.match(pattern, data)
            if match:
                return data
        raise forms.ValidationError(_('Invalid serial number'))
