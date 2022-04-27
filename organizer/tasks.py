# Create your tasks here

# from organizer.models import Widget

# from celery import shared_task


# @shared_task
# def add(x, y):
#     return x + y


# @shared_task
# def mul(x, y):
#     return x * y


# @shared_task
# def xsum(numbers):
#     return sum(numbers)


# @shared_task
# def count_widgets():
#     return Widget.objects.count()


# @shared_task
# def rename_widget(widget_id, name):
#     w = Widget.objects.get(id=widget_id)
#     w.name = name
#     w.save()

from django.contrib.auth import get_user_model
from celery import shared_task
from project import settings
from django.utils import timezone
from datetime import timedelta

#import logging
from project.celery import app
from django.template.loader import render_to_string
from django.core.mail import send_mail
import json

# # example
# @shared_task(bind=True)
# def test_func(self):
#     #operations
#     for i in range(10):
#         print(i)

#     return "Done"

# example
# @shared_task(bind=True)
# def send_mail_func(self):
#     user = get_user_model().objects.get(username='julian')

#     #timezone.localtime(users.date_time) + timedelta(days=2)

#     subject = "Test Subject"
#     message = "Test message - tutorial video part 2"
#     to_email = user.email
#     send_mail(
#         subject=subject, 
#         message=message, 
#         from_email=settings.EMAIL_HOST_USER,
#         recipient_list=[to_email],
#         fail_silently=True
#     )

#     return "Done"

@app.task 
def send_reminder_email(instance, email):
    instance_asJSON = json.loads(instance)
    subject = 'REMINDER: ' + instance_asJSON["fields"]["title"] + ' is due soon'
    message = instance_asJSON["fields"]["content"]
    
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[email], fail_silently=False)

    return "Sent"