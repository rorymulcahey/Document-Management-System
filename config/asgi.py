import os
from django.core.asgi import get_asgi_application

# Set the default settings module for ASGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
