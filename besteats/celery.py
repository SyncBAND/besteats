import os

from django.conf import settings

from celery import Celery


# Celery configuration
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "besteats.settings")
app = Celery("besteats")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
# sets the timezone for the entire Celery application
app.conf.timezone = settings.TIME_ZONE
