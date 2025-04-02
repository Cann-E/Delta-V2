import os  # lets us work with env vars

from django.core.wsgi import get_wsgi_application  # this sets up the WSGI app for Django

# sets the default settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delta.settings')

# creates the WSGI application object
application = get_wsgi_application()
