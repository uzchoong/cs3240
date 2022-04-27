from django.urls import path
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

from . import views
from django.views.generic.base import RedirectView

app_name = 'organizer'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),
    path('calendar/', views.defaultCalendar, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar, name='calendar-month'),
    path('calendar/goTo/', views.calendarGoTo, name='calendar-select'),
    path('classes/', views.ClassHomeView.as_view(), name='class-home'),
    path('classes/create/', views.ClassCreateView.as_view(), name='class-create'),
    path('classes/<pk>/', views.ClassDetailView.as_view(), name='class-detail'),
    path('classes/<pk>/join/', views.joinClass, name='class-join'),
    path('todo/', views.get_toDo, name='todo'),
    path('todo/list/', views.del_toDo, name='todo-list'),
    path('notes/', views.NoteHomeView.as_view(), name='note-home'),
    path('notes/upload/', views.UploadNoteView, name ='note-upload'),
    path('notes/changevisibility', views.ChangeNoteVisibility, name='note-change-visibility'),
    path('notes/all', views.NoteAllView.as_view(), name='note-all'),
    path('notes/<pk>/', views.NoteView.as_view(), name='note-edit'),
    path('notes/<pk>/delete/', views.deleteNote, name='note-delete'),

    #path('notes/all/major', views.NoteMajorView.as_view(), name='note-major'),

    # path('celerytest/', views.test, name="test"),
    # path('sendmail/', views.test_send_mail, name="sendmail"),
    # path('schedulemail/', views.schedule_mail, name="schedulemail")
    # path('classes/search', views.ClassSearchView.as_view(), name='search_result'),

    #added filters
    path('classes/index', views.ClassListView.as_view(), name='class-index'),
    path('notes/sortlist', views.NotesListView.as_view(), name='note-list'),

    # redirect URL to the home page
    path('', RedirectView.as_view(pattern_name='home', permanent=True), name='redirect-home')
] 


# celery -A project.celery worker --pool=solo -l info

# celery -A project beat -l INFO