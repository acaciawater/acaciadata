from django.shortcuts import get_object_or_404
from acacia.data.views import ProjectDetailView
from acacia.data.models import Project, ProjectLocatie, Dashboard, TabGroup

COL_LOOKUP = {'L': 'Watermeter Bron1 Uit 1 [0.1 m3]', 'M': 'Watermeter Bron1 Uit 2 [0.1 m3]', 'N': 'Watermeter Bron1 Uit 3 [0.1 m3]', 'O': 'Watermeter Bron1 Uit 4 [0.1 m3]',
               'P': 'Watermeter Bron2 Uit 1 [0.1 m3]', 'Q': 'Watermeter Bron2 Uit 2 [0.1 m3]', 'R': 'Watermeter Bron2 Uit 3 [0.1 m3]', 'S': 'Watermeter Bron2 Uit 4 [0.1 m3]'}

summary = {'Borgsweer': {
                         'debiet' : {'in': ['Systeem Bron in 1 0.1m3', 'Systeem Bron in 2 0.1m3'],
                                     'out': ['Watermeter Bron1 Uit 1 [0.1 m3]', 'Watermeter Bron1 Uit 2 [0.1 m3]', 'Watermeter Bron1 Uit 3 [0.1 m3]', 'Watermeter Bron1 Uit 4 [0.1 m3]',
                                             'Watermeter Bron2 Uit 1 [0.1 m3]', 'Watermeter Bron2 Uit 2 [0.1 m3]', 'Watermeter Bron2 Uit 3 [0.1 m3]', 'Watermeter Bron2 Uit 4 [0.1 m3]']
                         },
                         'ec': {'out': ['Systeem EC Bronuit1','Systeem EC Bronuit2'],
                                'in': ['Systeem EC Bron in',],
                                'maskout': ['Systeem onttrekken'],
                                'maskin' : ['Systeem Infiltreren']
                         }
                         },
           'Breezand': {
                         'debiet' : {'in': ['Bron1 in', 'Bron2 in', 'Bron3 in', 'Bron4 in'],
                                     'out': ['Bron1 uit','Bron2 uit', 'Bron3 uit', 'Bron4 uit']
                         },
                         'ec': {'out': ['Systeem 1 EC Bronuit',],
                                'in': ['Systeem EC Bron in',],
                                'maskout': ['Systeem 1 onttrekken'],
                                'maskin' : ['Systeem 1 Infiltreren']
                         }
                        }
           }


def get_series(series, name, mask=None):
    for s in series:
        if s.name == name:
            if mask is None: 
                return s.to_pandas()
            mask = get_series(series,mask)
            return s.to_pandas().where(mask>0)
    raise Exception(name)
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
            factor = 10 if 'weer'in key else 1
            names = values['debiet']['in']
            for name in names:
                series = get_series(locseries,name)
                sumin += series[-1]
            data[key]['debiet']['in'] = sumin/factor

            sumout = 0
            names = values['debiet']['out']
            for name in names:
                series = get_series(locseries,name)
                sumout += series[-1]
            data[key]['debiet']['out'] = sumout/factor

            ecin = 0
            names = values['ec']['in']
            masks = values['ec']['maskin']
            for mask,name in zip(masks,names):
                series = get_series(locseries,name,mask)
                ecin += series.mean()
            data[key]['ec']['in'] = ecin / len(names) * 10.0

            ecout = 0
            names = values['ec']['out']
            masks = values['ec']['maskout']
            for mask,name in zip(masks,names):
                series = get_series(locseries,name,mask)
                ecout += series.mean()
            data[key]['ec']['out'] = ecout / len(names) * 10.0
            
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

class DashView(TemplateView):
    template_name = 'data/dash.html'
    
    def get_context_data(self, **kwargs):
        context = super(DashView,self).get_context_data(**kwargs)
        name = context.get('name')
        dash = get_object_or_404(Dashboard, name__iexact=name)
        context['dashboard'] = dash
        return context    
    
class DashGroupView(TemplateView):
    template_name = 'dashgroup.html'
    
    def get_context_data(self, **kwargs):
        context = super(DashGroupView,self).get_context_data(**kwargs)
        name = context.get('name')
        page = int(self.request.GET.get('page', 1))
        group = get_object_or_404(TabGroup, name__iexact=name)
        dashboards =[p.dashboard for p in group.tabpage_set.order_by('order')]
        context['group'] = group
        page = min(page, len(dashboards))
        if page > 0:
            context['page'] = int(page)
            context['dashboard'] = dashboards[page-1]
        return context    
