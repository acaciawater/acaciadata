import StringIO
from xml.etree.ElementTree import ElementTree
import zipfile

from django.http.response import HttpResponse, HttpResponseServerError
from django.utils.text import slugify

from acacia.meetnet.bro.gmw import registration_request
from acacia.meetnet.models import Well
from acacia.meetnet.bro.models import Defaults
from django.views.generic import UpdateView
from django.urls.base import reverse
from acacia.meetnet.bro.models.registrationrequest import RegistrationRequest
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import ugettext_lazy as _
from acacia.meetnet.bro.models.groundwatermonitoringwell import GroundwaterMonitoringWell

def download_gmw(request):
    ''' download ZIP file with BRO registration requests for all wells '''
    io = StringIO.StringIO()
    zf = zipfile.ZipFile(io,'w')
    try:
        for well in Well.objects.all():
            try:
                query = well.bro.registrationrequest_set.all()
            except ObjectDoesNotExist:
                raise ValueError(_('No BRO information available for well %s' % well))
            if query.exists():
                reg = query.latest('modified')
                reg.update()
                reg.save()
            else:
                reg = RegistrationRequest.create_for_well(well, user=request.user)
            xml = reg.as_xml()
            zf.writestr(slugify(well.nitg or well.name) + '.xml', xml)
        zf.close()
        resp = HttpResponse(io.getvalue(), content_type = "application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=bro.zip'
    except Exception as e:
        resp = HttpResponseServerError(unicode(e))
    return resp

def download_gmw1(request):
    ''' download ZIP file with BRO registration requests for all wells '''
    io = StringIO.StringIO()
    zf = zipfile.ZipFile(io,'w')
    try:
        for well in Well.objects.all():
            request = ElementTree(registration_request(well))#,kvk='73552739'))
            xml = StringIO.StringIO()
            request.write(xml,xml_declaration=True,encoding='utf-8')
            zf.writestr(slugify(well.nitg or well.name) + '.xml', xml.getvalue())
        zf.close()
        resp = HttpResponse(io.getvalue(), content_type = "application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=bro.zip'
    except Exception as e:
        resp = HttpResponseServerError(unicode(e))
    return resp

class DefaultsView(UpdateView):
    model = Defaults
    fields = ('deliveryAccountableParty','owner','maintenanceResponsibleParty')
    
    def get_success_url(self):
        return self.request.GET.get('next',reverse('bro:gmw'))
    
    def get_context_data(self, **kwargs):
        return UpdateView.get_context_data(self, **kwargs)
    
    def form_valid(self, form):
        retval =  UpdateView.form_valid(self, form)

        # perform updates
        defaults = self.object
        RegistrationRequest.objects.filter(gmw__well__network=defaults.network).update(
            deliveryAccountableParty = defaults.deliveryAccountableParty
        )
        GroundwaterMonitoringWell.objects.filter(well__network=defaults.network).update(
            owner = defaults.owner,
            maintenanceResponsibleParty = defaults.maintenanceResponsibleParty
        )
        return retval
    