# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from acacia.meetnet.auth import StaffRequiredMixin
from django.views.generic.edit import FormView
from acacia.meetnet.sensor.forms import LoggerAddForm, LoggerMoveForm,\
    LoggerStartForm, LoggerStopForm
from acacia.meetnet.actions import update_screens
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from acacia.meetnet.models import Network, Datalogger, LoggerPos
from acacia.meetnet.sensor import admin
from django.urls.base import reverse
from django.views.generic.detail import DetailView
from acacia.meetnet.util import to_datetime

    
# Create your views here.
class LoggerAddView(StaffRequiredMixin, FormView):
    form_class = LoggerAddForm
    template_name = 'sensor/logger_add.html'

    def get_success_url(self):
        return reverse('sensor:add-done', args=(self.object.pk,))
    
    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)
        context['network'] = Network.objects.first()
        return context
    
    def get_initial(self):
        initial = FormView.get_initial(self)
        initial['start_date'] = str(timezone.localdate())
        initial['start_time'] = timezone.localtime()
        return initial
    
    def form_valid(self, form):
        try:
            install = self.add_logger(form.cleaned_data)
            for d in install.logger.datasources:
                d.download()
            update_screens(None, self.request, [install.screen])
            self.object = install
        except IntegrityError as e:
            raise ValidationError(e)
        return FormView.form_valid(self, form)
    
    def add_logger(self, data):
        serial = data['serial']
        model = data['model']
        screen = data['screen']
        depth = data['depth']
        refpnt = data['refpnt']
        start = data['start']
        logger = admin.create(serial, model)
        return admin.install(logger, screen, start, depth, refpnt)

class LoggerStopView(StaffRequiredMixin, FormView):
    form_class=LoggerStopForm
    template_name = 'sensor/logger_stop.html'
    
    def get_success_url(self):
        return reverse('sensor:stop-done', args=(self.object.pk,))

    def get_initial(self):
        initial = FormView.get_initial(self)
        initial['stop_date'] = str(timezone.localdate())
        initial['stop_time'] = "12:00:00"
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        logger = data['logger']
        date = to_datetime(data['stop_date'], data['stop_time'])
        result = admin.stop(logger, date)
        if result.exists():
            self.object = logger
        else:
            self.object = None
        return FormView.form_valid(self, form)

class LoggerStartView(StaffRequiredMixin, FormView):
    form_class=LoggerStartForm
    template_name = 'sensor/logger_start.html'

    def get_success_url(self):
        return reverse('sensor:start-done')

    def get_initial(self):
        initial = FormView.get_initial(self)
        initial['start_date'] = str(timezone.localdate())
        initial['start_time'] = timezone.localtime()
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        logger = data['logger']
        date = to_datetime(data['start_date'], data['start_time'])
        result = admin.start(logger, date)
        if result.exists():
            self.object = logger
        else:
            self.object = None
        return FormView.form_valid(self, form)

class LoggerMoveView(StaffRequiredMixin, FormView):
    form_class = LoggerMoveForm
    template_name = 'sensor/logger_move.html'

    def get_success_url(self):
        return reverse('sensor:move-done', args=(self.object.pk,))
    
    def get_context_data(self, **kwargs):
        context = FormView.get_context_data(self, **kwargs)
        context['network'] = Network.objects.first()
        return context
    
    def get_initial(self):
        initial = FormView.get_initial(self)
        initial['stop_date'] = str(timezone.localdate())
        initial['stop_time'] = '12:00:00'
        initial['start_date'] = str(timezone.localdate())
        initial['start_time'] = timezone.localtime()
        return initial
    
    def form_valid(self, form):
        try:
            curpos, newpos = self.move_logger(form.cleaned_data)
            self.object = newpos
        except IntegrityError as e:
            raise ValidationError(e)
        return FormView.form_valid(self, form)
    

    def move_logger(self, data):
        logger = data['logger']
        stop = to_datetime(data['stop_date'], data['stop_time'])
        screen = data['screen']
        depth = data['depth']
        refpnt = data['refpnt']
        start = to_datetime(data['start_date'],data['start_time'])
        return admin.move(logger, screen, start, stop=stop, depth=depth, refpnt=refpnt)
        
class LoggerAddedView(DetailView):
    model = LoggerPos
    template_name = 'sensor/logger_added.html'

class LoggerMovedView(DetailView):
    model = LoggerPos
    template_name = 'sensor/logger_moved.html'

class LoggerStartedView(DetailView):
    model = Datalogger
    template_name = 'sensor/logger_started.html'

class LoggerStoppedView(DetailView):
    model = Datalogger
    template_name = 'sensor/logger_stopped.html'
        
