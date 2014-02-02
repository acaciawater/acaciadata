from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from models import DataFile

import logging
logger = logging.getLogger(__name__)

class DataFileAddView(CreateView):
    model = DataFile
    fields = ['file',]

class DataFileDetailView(DetailView):
    model = DataFile
