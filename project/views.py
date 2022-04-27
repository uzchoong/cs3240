from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from organizer.models import Note, Calendar, Profile
from django.utils import timezone
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User

from django.http import FileResponse, Http404

# https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#operator
# https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-editing/
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/

# https://docs.djangoproject.com/en/3.2/topics/http/shortcuts/
def redirect_HomeView(request):
    if (request.user.is_authenticated and request.user.profile.computingID == ''):
        return redirect(reverse('edit-profile', args=[request.user.profile.id]))
    else:
        return render(request, 'index.html')


class ProfileEditView(generic.UpdateView):
    model = Profile
    template_name = 'edit-profile.html'

    fields = ['computingID', 'major']
    success_url = '/'
