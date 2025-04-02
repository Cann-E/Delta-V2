import os

from django.core.asgi import get_asgi_application

# set the default settings file for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delta.settings')

#  get ASGI application for deployment (used for async servers)
application = get_asgi_application()
