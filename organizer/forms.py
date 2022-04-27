from django import forms
from django.db.models import fields

from .models import ToDo, Note

from django.core.exceptions import ValidationError
from django.utils import timezone

from datetimewidget.widgets import DateTimeWidget

# https://pypi.org/project/django-datetime-widget2/
# https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/
class toDoForm(forms.ModelForm):
    class Meta:
        model = ToDo
        exclude = ['user', 'created']
        fields = ('title', 'content', 'dueDate', 'remindTime')
        labels = {
            'title': 'Title:',
            'content': 'Description:',
            'dueDate': 'Due Date and Time:',
            'remindTime': 'Notification time before due (a reminder email will be sent):'
        }
        dateTimeOptions = {
            'format': 'mm/dd/yyyy HH:ii P',
            'autoclose': True,
            'showMeridian' : True,
            'minuteStep': 10,
            'todayHighlight': True,
        }
        widgets = {
            #Use localization and bootstrap 3
            'dueDate': DateTimeWidget(attrs={'id':"yourdatetimeid"}, usel10n=True, options=dateTimeOptions)
            #'dueDate': DateTimeWidget(options = dateTimeOptions)
        }

    # validate that the dueDate is at least remindTime min into the future, so that a reminder can be sent
    # https://stackoverflow.com/questions/43920328/data-returning-none-in-django-with-appended-select-field-in-js
    def clean(self):
        theDueDate = self.cleaned_data.get('dueDate')
        theRemindTime = self.cleaned_data.get('remindTime')
        #print((data - timezone.now()).total_seconds())
        if (theDueDate - timezone.now()).total_seconds()/60 <= theRemindTime:
            raise ValidationError("Set a valid time so your reminder can be sent!")

class UploadNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['user']
        fields = ('title', 'file', 'theClass', 'isVisible')
        labels = {
            'title': 'Title:',
            'file': 'File',
            'theClass': 'Class',
            'isVisible': 'Visible to others in the class'
        }