import django_filters
from django.db.models import Q

from .models import Classes, Note, Profile, User

#https://www.youtube.com/watch?v=nle3u6Ww6Xk
#https://simpleisbetterthancomplex.com/tutorial/2016/11/28/how-to-filter-querysets-dynamically.html

class ClassFilter(django_filters.FilterSet):
    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending')
    )
    # make order by credits
    credit_ordering = django_filters.ChoiceFilter(label='Credits', choices=CHOICES, method='filter_by_credits')

    major_ordering = django_filters.ChoiceFilter(label='Department', choices=Classes.DEPARTMENT_CHOICES,
                                                 method='filter_by_major')

    name_search = django_filters.CharFilter(method='name_or_code', label='Name')

    professor_search = django_filters.CharFilter(method='professor_contains_search', label='Professor')

    class Meta:
        model = Classes

        fields = ['name_search', 'professor_search']

    def filter_by_credits(self, queryset, name, value):
        expression = 'credits' if value == 'ascending' else '-credits'
        return queryset.order_by(expression)

    def name_or_code(self, queryset, name, value):
        return Classes.objects.filter(
            Q(name__icontains=value)
        )

    def professor_contains_search(self, queryset, name, value):
        return Classes.objects.filter(
            Q(professor__icontains=value)
        )

    def filter_by_major(self, queryset, name, value):
        q = Classes.objects.filter(code=value)
        return q


class NotesFilter(django_filters.FilterSet):
    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending')
    )

    # make order by class/title
    ordering = django_filters.ChoiceFilter(label='Class', choices=CHOICES, method='filter_by_Class')

    ordering2 = django_filters.ChoiceFilter(label='Title', choices=CHOICES, method='filter_by_title')

    class Meta:
        model = Note

        fields = {
            'title': ['icontains'],
        }

    def filter_by_Class(user, queryset, theClass, value):
        expression = 'theClass' if value == 'ascending' else '-theClass'
        return queryset.order_by(expression)

    def filter_by_title(user, queryset, title, value):
        expression = 'title' if value == 'ascending' else '-title'
        return queryset.order_by(expression)


class NotesAllFilter(django_filters.FilterSet):
    CHOICES = (
        ('all_notes', 'All Notes'),
        ('major_notes', 'My major notes'),
    )

    department_filtering = django_filters.ChoiceFilter(label='Department', choices=Classes.DEPARTMENT_CHOICES,
                                                       method='filter_by_department')

    major_filtering = django_filters.ChoiceFilter(label='By Major', choices=Profile.MAJOR_CHOICES, method='filter_by_major')

    def filter_by_department(self, queryset, name, value):
        q = Note.objects.filter(theClass__code=value)
        return q


    def filter_by_major(self, queryset, name, value):
        return Note.objects.filter(user__profile__major=value)

#    def __init__(self, *args, **kwargs):
#        user = kwargs.pop('user', None)
#        super(NotesAllFilter, self).__init__(*args, **kwargs)
#        if user is not None:
#            self.request.user

class MajorFilter(django_filters.FilterSet):

    department_filtering = django_filters.ChoiceFilter(label='Department', choices=Classes.DEPARTMENT_CHOICES,
                                                       method='filter_by_department')

    def filter_by_department(self, queryset, name, value):
        q = Note.objects.filter(theClass__code=value)
        return q