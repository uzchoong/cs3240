from datetime import datetime, timedelta
import holidays
from calendar import HTMLCalendar
from .models import ToDo
from .forms import toDoForm

# https://www.huiwenteo.com/normal/2018/07/24/django-calendar.html
# https://pypi.org/project/holidays/
# https://stackoverflow.com/questions/65391958/why-is-an-item-displying-at-the-very-bottom-of-a-django-template-page
class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user=None):
        self.year = year
        self.month = month
        self.user = user
        super(Calendar, self).__init__()

    # filter todos by day
    def formatday(self, day, todos, hol):
        todos_per_day = todos.filter(dueDate__day=day)
        d = ''
        for date, holiday in hol.items():
            if date.day == day:
                d += f'<a style="color:red"><b> {holiday} </b></a>'
        for todo in todos_per_day:
            d += f'<li> {todo.title} </li>'
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    def formatweek(self, theweek, todos, hol):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, todos, hol)
        return f'<tr> {week} </tr>'

    # filter events by year and month
    def formatmonth(self, withyear=True):
        todos = ToDo.objects.filter(dueDate__year=self.year, dueDate__month=self.month, user=self.user)

        hol = {}
        for date, holiday in holidays.US(years=self.year, observed=False).items():
            if date.month == self.month:
                hol[date] = holiday

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, todos, hol)}\n'
        cal += f'</table>'
        return cal
