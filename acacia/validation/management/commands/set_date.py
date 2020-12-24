from django.core.management.base import BaseCommand
from acacia.data.models import Series
from acacia.validation.models import Validation
from django.contrib.auth.models import User
import dateutil
from django.utils.timezone import make_aware
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Sets date of last validation'
    
    def add_arguments(self, parser):
        parser.add_argument('-r','--regex',
                dest='regex',
                default=None,
                help="Regular expression to filter series by name, e.g. 'vs\d{2}' ")
        parser.add_argument('date', help = 'Date of validation')

    def handle(self, *args, **options):
        date = make_aware(dateutil.parser.parse(options.get('date')))
        regex = options.get('regex')
        user = User.objects.filter(is_superuser=True).first()
        queryset=Series.objects.all()
        if regex:
            queryset = queryset.filter(name__iregex=regex)
        for s in queryset:
            logger.info(str(s))
            if s.aantal() > 0:
                start = s.van()
                stop = s.tot()
                try:
                    val = s.validation
                except:
                    val = Validation.objects.create(series=s)
                val.accept(user,(start,min(stop,date)))
        