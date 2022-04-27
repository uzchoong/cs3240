from django.db.models import Q
from .filters import ClassFilter, NotesFilter, NotesAllFilter, MajorFilter
from django.http import HttpResponseRedirect, request
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Note, Calendar, Profile, ToDo, Classes
from .forms import toDoForm, UploadNoteForm
from .utils import Calendar
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import os

os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAWGN3XIVBPUJESSLJ'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
os.environ['AWS_STORAGE_BUCKET_NAME'] = 'neworganizer-a18'
#from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
import boto3


class IndexView(generic.TemplateView):
    template_name = 'organizer/index.html'

class CalendarView(generic.ListView):
    model = Calendar
    template_name = 'organizer/assignments/calendar.html'
    context_object_name = 'latest_thought_list'

    def get_queryset(self):
        return Calendar.objects.all()

class ClassHomeView(generic.TemplateView):
    template_name = 'organizer/class_home.html'

# https://docs.djangoproject.com/en/3.2/topics/db/examples/many_to_many/
class ClassDetailView(generic.DetailView):
    model = Classes
    template_name = 'organizer/class_detail.html'
    context_object_name = 'classes'

# https://docs.djangoproject.com/en/3.2/topics/http/urls/#topics-http-reversing-url-namespaces
class ClassCreateView(generic.CreateView):
    model = Classes
    template_name = 'organizer/class_create.html'
    fields = ['name', 'credits', 'code', 'courseNumber', 'year', 'professor']
    
    # success_url = reverse('organizer:class-home')
    success_url = '/organizer/classes/' # change to reverse() - doesn't work???

# https://docs.djangoproject.com/en/3.2/topics/db/queries/
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-display/
class ClassIndexView(generic.ListView):
    model = Classes
    template_name = 'organizer/class_index.html'
    context_object_name = 'classes'


def joinClass(request, pk):
    classToJoin = get_object_or_404(Classes,pk=pk)

    classToJoin.user.add(request.user)

    return redirect(reverse('organizer:class-home'))

class ToDoView(generic.ListView):
    model = ToDo
    template_name = 'organizer/todo.html'

class ToDoListView(generic.ListView):
    model = ToDo
    template_name = 'organizer/todo-list.html'

# https://stackoverflow.com/questions/18246326/how-do-i-set-user-field-in-form-to-the-currently-logged-in-user
# https://stackoverflow.com/questions/12848605/django-modelform-what-is-savecommit-false-used-for
# https://stackoverflow.com/questions/569468/django-multiple-models-in-one-template-using-forms/575133#575133
# https://stackoverflow.com/questions/20170062/displaying-django-form-validation-errors-for-modelforms
def get_toDo(request):
    if request.method == "POST":
        tD = toDoForm(request.POST)
        if tD.is_valid():
            theToDo = tD.save(commit=False) # commit=False so the User can be set to the current User automatically
            theToDo.user = User.objects.get(username=request.user.username) 
            theToDo.save()
            return HttpResponseRedirect(reverse('organizer:todo-list'))  # UPDATE TO SHOW CONFIRMATION
        else:
            return HttpResponse(tD.errors.values())  # error message - set it to display as a popup

    tD = toDoForm()
    return render(request, 'organizer/todo.html', {'form': tD})

# https://stackoverflow.com/questions/5895588/django-multivaluedictkeyerror-error-how-do-i-deal-with-it
# https://stackoverflow.com/questions/68113852/how-to-check-whether-the-checkbox-is-checked-in-django
# https://stackoverflow.com/questions/6223149/django-post-checkbox-data
def del_toDo(request):
    if request.user.is_authenticated:
        todos = ToDo.objects.filter(user=request.user)

        if request.method == "POST":
            todo = toDoForm(request.POST)
            #if "toDoDelete" in request.POST: 
            if "checkedbox" in request.POST:  # handles MultiValueDictKeyError if nothing is selected when attempting to delete
                checkedlist = request.POST.getlist('checkedbox')
                for todo_id in checkedlist:
                    #print(todo_id)
                    todo = ToDo.objects.get(id=todo_id)
                    todo.delete()
                return HttpResponseRedirect(reverse('organizer:todo-list'))

            else:
                pass # IMPLEMENT POPUP WARNING HERE!!!!!
        else:
            todo = toDoForm()

        return render(request, 'organizer/todo-list.html', {'objs': todos, 'form': todo})
    else:
        return HttpResponseRedirect(reverse('home'))


# https://docs.djangoproject.com/en/3.2/topics/http/file-uploads/
def UploadNoteView(request):
    if request.method == 'POST':
        form = UploadNoteForm(request.POST, request.FILES)
        if form.is_valid():
            theNote = form.save(commit=False)
            theNote.user = User.objects.get(username=request.user.username)
            theNote.save()
            return redirect(reverse('organizer:note-home')) # UPDATE TO DISPLAY SUCCESS MESSAGE, REDIRECT
    else:
        form = UploadNoteForm()
        context = {
            'form':form,
        }
    return render(request, 'organizer/note-upload.html', context)

def ChangeNoteVisibility(request):
    if request.method == "POST": 
            if "checkedbox" in request.POST:  # handles MultiValueDictKeyError if nothing is selected when attempting to delete
                checkedlist = request.POST.getlist('checkedbox')
                for note_id in checkedlist:
                    note = Note.objects.get(id=note_id)
                    note.isVisible = (not note.isVisible)
                    note.save()
                    return HttpResponseRedirect(reverse('organizer:note-home'))
            else:
                pass # IMPLEMENT POPUP WARNING HERE!!!!!

    return redirect(reverse('organizer:note-home'))        

class NoteHomeView(generic.TemplateView):
    template_name = 'organizer/note-home.html'

class NoteView(generic.DetailView):
    model = Note
    template_name = 'organizer/note-detail.html'
    context_object_name = 'note'

def deleteNote(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return redirect(reverse('organizer:note-home'))

class NoteAllView(generic.ListView):
    model = Note
    template_name = 'organizer/note-all.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NotesAllFilter(self.request.GET, queryset=self.get_queryset())
        return context

class NoteMajorView(generic.ListView):
    model = Note
    template_name = 'organizer/note-major.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user__profile__major=self.request.user.profile.major)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = MajorFilter(self.request.GET, queryset=self.get_queryset())
        return context

#def download_file(file_name):
    # s3 = boto3.client('s3')
    # s3.download_file('a18-organizer-new', file_name, 'media/' + file_name)

    # return redirect('media/' + file_name)

# https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html
def calendar(request, year, month):

    if request.user.is_authenticated:
        # cal = HTMLCalendar().formatmonth(year, month)
        cal = Calendar(year, month, request.user).formatmonth(withyear=True)

        next_year = year
        previous_year = year

        # jump to previous year
        if(month - 1 < 1):
            prev_month = 12
            previous_year = year - 1
        else:
            prev_month = month - 1
            previous_year = year

        # jump to next year
        if(month + 1 > 12):
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year

        return render(request, 'organizer/assignments/calendar.html',
                    {
                        'prev_month': prev_month,
                        'next_month': next_month,
                        'next_year': next_year,
                        'previous_year': previous_year,
                        'month': month,
                        'cal': cal,
                    })
    else:
        return HttpResponseRedirect(reverse('home'))

# https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html
def defaultCalendar(request):
    if request.user.is_authenticated:
        today = timezone.now()
        cal = Calendar(today.year, today.month, request.user).formatmonth(withyear=True)

        next_year = today.year
        previous_year = today.year

        # jump to previous year
        if(today.month - 1 < 1):
            prev_month = 12
            previous_year = today.year - 1
        else:
            prev_month = today.month - 1

        # jump to next year
        if(today.month + 1 > 12):
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1

        return render(request, 'organizer/assignments/calendar.html',
                    {
                        'next_year': next_year,
                        'previous_year': previous_year,
                        'month': today.month,
                        'prev_month': prev_month,
                        'next_month': next_month,
                        "cal": cal,
                    })
    else:
        return HttpResponseRedirect(reverse('home'))

# https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html
def calendarGoTo(request):

    if request.user.is_authenticated:
        if request.method == "POST":
            today = timezone.now()
            try:    # if valid input
                year = int(request.POST.get('select_year'))
            except ValueError:  # invalid year input
                year = today.year   # defaults to current year

            if request.POST.get('select_month') == "none": # month selected
                month = today.month
            else:   # no month selected -- defaults to current month
                month = int(request.POST.get('select_month'))

            try:
                cal = Calendar(year, month, request.user).formatmonth(withyear=True)
            except ValueError:  # invalid year input
                cal = Calendar(today.year, month, request.user).formatmonth(withyear=True)

            next_year = year
            previous_year = year

            # jump to previous year
            if(month - 1 < 1):
                prev_month = 12
                previous_year = year - 1
            else:
                prev_month = month - 1

            # jump to next year
            if(month + 1 > 12):
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1

            return render(request, 'organizer/assignments/calendar.html',
                        {
                            'next_year': next_year,
                            'previous_year': previous_year,
                            'month': month,
                            'prev_month': prev_month,
                            'next_month': next_month,
                            "cal": cal,
                        })
    else:
        return HttpResponseRedirect(reverse('home'))


#https://docs.djangoproject.com/en/3.2/ref/models/querysets/#std:fieldlookup-icontains
#https://simpleisbetterthancomplex.com/tutorial/2016/11/28/how-to-filter-querysets-dynamically.html
#filter for class
class ClassListView(generic.ListView):
    model = Classes
    template_name = 'organizer/class_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ClassFilter(self.request.GET, queryset=self.get_queryset())
        return context

#filter for Notes
class NotesListView(generic.ListView):
    model = Note
    template_name = 'organizer/note_sort_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NotesFilter(self.request.GET, queryset=self.get_queryset())
        return context

#class ClassListView(generic.ListView):
#    model = Classes
#    template_name = 'organizer:class_search'

# def test(request):
#     test_func.delay()
#     return HttpResponse("Done")

# def test_send_mail(request):
#     send_mail_func.delay()
#     return HttpResponse("Sent")

# def schedule_mail(request):
#     schedule, created = CrontabSchedule.objects.get_or_create(hour=1, minute=41)
#     task = PeriodicTask.objects.create(crontab=schedule, name="schedule_mail_task_"+"6", task='organizer.tasks.send_mail_func')#, args = json.dumps([[2,3]]))  # use some ID/pk, etc to make it unique (1 used as an example)
#     return HttpResponse("Done")