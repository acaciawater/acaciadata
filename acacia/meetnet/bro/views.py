import StringIO
from xml.etree.ElementTree import ElementTree
import zipfile

from django.http.response import HttpResponse, HttpResponseServerError
from django.utils.text import slugify

from acacia.meetnet.bro.gmw import registration_request
from acacia.meetnet.models import Well


def download_gmw(request):
    ''' download ZIP file with BRO registration requests for all wells '''
    io = StringIO.StringIO()
    zf = zipfile.ZipFile(io,'w')
    try:
        for well in Well.objects.all():
            request = ElementTree(registration_request(well,kvk='73552739'))
            xml = StringIO.StringIO()
            request.write(xml,xml_declaration=True,encoding='utf-8')
            zf.writestr(slugify(well.nitg or well.name) + '.xml', xml.getvalue())
        zf.close()
        resp = HttpResponse(io.getvalue(), content_type = "application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=bro.zip'
    except Exception as e:
        resp = HttpResponseServerError(unicode(e))
    return resp
