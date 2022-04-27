from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.conf.enable_utc = False

app.conf.update(timezone = 'America/New_York')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

#Celery Beat Settings
# app.conf.beat_schedule = {

#     # can hard-code a one-time message by specifying all time fields (e.g. hour, minute, day_of_month, month_of_year, etc)
#     # if other fields aren't specified, default to "*": repeat
#     # or, dynamically send messages (for reminders)
#     # make schedule names unique
#     'send-mail-every-day-at-8': {
#         'task': 'organizer.tasks.send_mail_func',
#         'schedule': crontab(hour=0, minute=55),
#         #'args': (2,)
#     }
# }

#celery documentation - https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')