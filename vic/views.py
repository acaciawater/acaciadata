from django.shortcuts import get_object_or_404
from spaarwater.views import SpaarwaterDetailView, DashGroupView
from acacia.data.models import Project

class VICDetailView(SpaarwaterDetailView):
    template_name = 'vic_detail.html'

    def get_object(self):
        return get_object_or_404(Project,name='VIC')

class VICGroupView(DashGroupView):
    template_name = 'vic_dashgroup.html'