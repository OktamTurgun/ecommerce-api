import os
from django.core.wsgi import get_wsgi_application

# Auto-detect Railway
if os.getenv('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()
