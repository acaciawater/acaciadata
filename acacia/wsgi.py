"""
WSGI config for acacia project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/theo/acacia-data/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
#sys.path.append('/home/django_projects/MyProject')
#sys.path.append('/home/django_projects/MyProject/myproject')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acacia.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
