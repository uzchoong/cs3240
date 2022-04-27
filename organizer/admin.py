from django.contrib import admin

from .models import Note, Classes, Calendar, ToDo

from .models import Profile

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

admin.site.register(Note)
admin.site.register(Calendar)
admin.site.register(Classes)
admin.site.register(ToDo)

class NoteInline(admin.TabularInline):
    model = Note

class CalendarInline(admin.TabularInline):
    model = Calendar

# need way to show Classes in admin page, b/c it has a Many-to-Many relationship w/User
class ClassOrderAdmin(admin.ModelAdmin):
    fields = ['name', 'user']
    list_display = ('name', 'get_user')

    def get_user(self, obj):
        return "\n".join([u.user for u in obj.user.all()])


# adds Profile model's fields to User page in admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, NoteInline, CalendarInline)

# re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


