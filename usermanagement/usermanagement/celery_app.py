from django.conf import settings
from celery import Celery
import django
import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "usermanagement.settings")

django.setup()


app = Celery("usermanagement")

app.config_from_object("django.conf:settings", namespace="CELERY")

import user.celery_task

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)