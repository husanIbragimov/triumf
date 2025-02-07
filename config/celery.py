import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
SECRET_KEY = os.environ.get('SECRET_KEY')

app = Celery('triumf')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
