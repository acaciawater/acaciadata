SECRET_KEY = 'lyh)8hhwcz*a7i-o9ndk(7j0(%e25o3ji^7e+anqq4e)f^7#y('
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'acaciadata',                      # Or path to database file if using sqlite3.
        'USER': 'acacia',                      # Not used with sqlite3.
        'PASSWORD': 'Beaumont1',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST='acaciadata.com'
EMAIL_PORT=25
EMAIL_HOST_USER='webmaster@acaciadata.com'
EMAIL_HOST_PASSWORD='acaciawater'
EMAIL_USE_TLS = True
