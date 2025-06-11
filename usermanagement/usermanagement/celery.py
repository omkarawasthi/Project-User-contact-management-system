import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contact_project.settings')

app = Celery('usermanagement')
app.config_from_object('django.conf:settings', namespace='CELERY')
