import os
import shutil
import logging

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from acacia.data.upload import sourcefile_upload
from acacia.data.models import SourceFile
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Move source files to correct media folder'

    def handle(self, *args, **options):
        storage = default_storage
        for sf in SourceFile.objects.all():
            correct = sourcefile_upload(sf, os.path.basename(sf.file.name))
            if sf.file.name != correct:
#                 print (sf.file.name, correct)
                src = storage.path(sf.file.name)
                dst = storage.path(correct)
                logger.info(src)
                logger.info(dst)
                destdir = os.path.dirname(dst)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                sf.file.name = correct
                sf.save(update_fields = ['file'])
                try:
                    shutil.move(src, dst)
                except Exception as e:
                    logger.error(e)