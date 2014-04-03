from django.shortcuts import get_object_or_404
from acacia.data.views import ProjectDetailView
from acacia.data.models import Project, ProjectLocatie, Dashboard

summary = {'Borgsweer': {
                         'debiet' : {'in': ['Systeem Bron in 1 0.1m3', 'Systeem Bron in 2 0.1m3'],
                                     'out': ['Systeem Openzandfilter  0.1m3',]
                         },
                         'ec': {'out': ['Systeem EC Bronuit1','Systeem EC Bronuit2'],
                                'in': ['Systeem EC Bron in',]
                         }
                         },
           'Breezand': {
                         'debiet' : {'in': ['Systeem Bron in 1 0.1m3', 'Systeem Bron in 2 0.1m3', 'Systeem Bron in 3 0.1m3', 'Systeem Bron in 4 0.1m3'],
                                     'out': ['Systeem Bron Uit 1 0.1m3','Systeem Bron Uit 2 0.1m3', 'Systeem Bron Uit 3 0.1m3', 'Systeem Bron Uit 3 0.1m3']
                         },
                         'ec': {'out': ['Systeem 1 EC Bronuit',],
                                'in': ['Systeem EC Bron in',]
                         }
                        }
           }


def get_series(series, name):
    for s in series:
        if s.name == name: 
            return s
    return None

class SpaarwaterDetailView(ProjectDetailView):
    
    template_name = 'spaarwater.html'

    def get_summary_data(self):
        data = {}
        for key,values in summary.items():
            loc = ProjectLocatie.objects.get(name=key)
            locseries = loc.series()
            data[key] = {'debiet': {'in': 0, 'out': 0}, 'ec': {'in': 0, 'out': 0}}
            sumin = 0
            names = values['debiet']['in']
            for name in names:
                series = get_series(locseries,name)
                sumin += series.laatste().value# - series.eerste().value
            data[key]['debiet']['in'] = sumin/10

            sumout = 0
            names = values['debiet']['out']
            for name in names:
                series = get_series(locseries,name)
                sumout += series.laatste().value# - series.eerste().value
            data[key]['debiet']['out'] = sumout/10

            ecin = 0
            names = values['ec']['in']
            for name in names:
                series = get_series(locseries,name)
                ecin += series.gemiddelde()
            data[key]['ec']['in'] = ecin / len(names)

            ecout = 0
            names = values['ec']['out']
            for name in names:
                series = get_series(locseries,name)
                ecout += series.gemiddelde()
            data[key]['ec']['out'] = ecout / len(names)
            
        return data

    def get_context_data(self, **kwargs):
        context = super(SpaarwaterDetailView,self).get_context_data(**kwargs)
        context['summary'] = self.get_summary_data()
        return context
    
    def get_object(self):
        return get_object_or_404(Project,name='Spaarwater')
    
# from acacia.data.views import MeetLocatieDetailView
#     
# class BreezandView(MeetLocatieDetailView):
#     def get_object(self):
#         return get_object_or_404(MeetLocatie, pk=2)

from django.views.generic.base import TemplateView

class BreezandView(TemplateView):
    template_name = 'data/dash.html'
    
    def get_context_data(self, **kwargs):
        context = super(BreezandView,self).get_context_data(**kwargs)
        dash = get_object_or_404(Dashboard, name='Breezand')
        context['dashboard'] = dash
        return context    