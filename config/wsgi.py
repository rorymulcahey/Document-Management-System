import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
