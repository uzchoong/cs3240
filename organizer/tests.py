import datetime
import unittest

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Note, Calendar, Profile, Classes, ToDo
from .utils import Calendar
from .forms import toDoForm
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# from django.db.models import Model
# from django.core.exceptions import ObjectDoesNotExist

#https://stackoverflow.com/questions/2581005/django-testcase-testing-order/2581056
# https://docs.djangoproject.com/en/3.2/topics/testing/tools/
# https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#auth-custom-user
# https://docs.djangoproject.com/en/3.2/topics/auth/default/
# https://docs.djangoproject.com/en/3.2/ref/contrib/auth/
# https://stackoverflow.com/questions/63054997/difference-between-user-objects-create-user-vs-user-objects-create-vs-user
class TestLogin(TestCase):
    global_client = Client()
    # if User model is overridden, may need to use userModel.objects.create(username), then manually use set_password(password) 
    def setUp(self):
        userModel = get_user_model() # to get correct model if User is overridden
        user = userModel.objects.create_user(username='testLogin', password='password')
        user.save()

    def test_loginSuccess(self):
        c = Client()
        loginSuccess = c.login(username='testLogin', password='password')
        self.assertTrue(loginSuccess)

    def test_loginFailure(self):
        c = Client()
        loginFail = c.login(username='invalidUser', password='invalidPassword')
        self.assertFalse(loginFail)

    def test_secondFailure(self):
        self.assertFalse(self.global_client.login(username='notRealUser', password='notRealPassWord'))

    # def test_logout(self):
    #     c = Client()
        
    #     userModel = get_user_model()
    #     user = userModel.objects.get(username='testLogin')

    #     c.login(username='testLogin', password='password')

    #     c.logout()
    #     # is_authenticated() is true for every User; false for every AnonymousUser - no easy way to test if logged out?

# https://stackoverflow.com/questions/48814830/how-to-test-djangos-updateview
# https://docs.djangoproject.com/en/3.2/ref/models/instances/
class TestProfileEditor(TestCase):
    def setUp(self):
        userModel = get_user_model()
        user = userModel.objects.create_user(username='testLogin', password='password')
        user.save()

    def test_computingID_edit(self):
        user = User.objects.get(username='testLogin')
        c = Client()
        response = c.post(reverse('edit-profile', args=[user.profile.id]), {'computingID': 'abcdefg', 'major': 'HIST'})
        self.assertEquals(response.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEquals(user.profile.computingID, 'abcdefg')
        
    def test_major_edit(self):
        user = User.objects.get(username='testLogin')
        c = Client()
        response = c.post(reverse('edit-profile', args=[user.profile.id]), {'computingID': 'abcdefg', 'major': 'HIST'})
        self.assertEquals(response.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEquals(user.profile.major, 'HIST')

# https://docs.djangoproject.com/en/3.2/ref/models/querysets/#exists
class TestClasses(TestCase):
    def setUp(self):
        userModel = get_user_model()
        user = userModel.objects.create_user(username='testLogin', password='password')
        user.save()

    def test_ClassCreation(self):
        user = User.objects.get(username='testLogin')
        c = Client()
        response = c.post(reverse('organizer:class-create'), {'name': 'testName', 'credits': 3, 'code': 'CS', 'courseNumber': '9999', 'year': 2021, 'professor': 'testProf'})
        self.assertEqual(response.status_code, 302)
        testClass = Classes.objects.get(name='testName')
        self.assertEqual(testClass.name, 'testName')
        self.assertEqual(testClass.credits, 3)
        self.assertEqual(testClass.code, 'CS')
        self.assertEqual(testClass.courseNumber, '9999')
        self.assertEqual(testClass.year, 2021)
        self.assertEqual(testClass.professor, 'testProf')

    def test_ClassCreationFail(self):
        user = User.objects.get(username='testLogin')
        c = Client()
        response = c.post(reverse('organizer:class-create'), {'name': 'testName', 'credits': -3, 'code': 'CS', 'courseNumber': '-1', 'year': 1900, 'professor': 'testProf'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Classes.objects.exists()) 

    def test_ClassJoin(self):
        testUser = User.objects.get(username='testLogin')
        c = Client()
        response = c.post(reverse('organizer:class-create'), {'name': 'testName', 'credits': 3, 'code': 'CS', 'courseNumber': '9999', 'year': 2021, 'professor': 'testProf'})
        self.assertEqual(response.status_code, 302)
        testClass = Classes.objects.get(name='testName')

        # edit to use URLs?

        testClass.user.add(testUser)
        self.assertEqual(testClass.user.all().get(username=testUser.username), testUser)

    def test_ClassIndex(self):
        pass



class ToDoTests(TestCase):
    def setUp(self):
        userModel = get_user_model()
        user = userModel.objects.create_user(username='testLogin', password='password')
        user.save()

    def test_ToDoCreate(self):
        """
        Todo with valid data is displayed
        """
        form_data = {'title': 'testCase',
                        'content': 'test',
                        'created': timezone.now(),
                        'dueDate': timezone.now()+timedelta(hours=2),
                        'remindTime': 30}
        testToDo = toDoForm(data=form_data)
        self.assertTrue(testToDo.is_valid())

        self.assertEqual(testToDo.cleaned_data.get('title'), "testCase")
        self.assertEqual(testToDo.cleaned_data.get('content'), "test")
        # self.assertAlmostEqual(testToDo.cleaned_data.get('dueDate'), timezone.now(), delta=datetime.timedelta(seconds=1))
        # fix later - cannot create ToDo w/dueDate < 10min in the future


    def test_ToDoCreateFail(self):
        """
        Todo with invalid data is not displayed
        """
        form_data = {'title': '',
                        'content': '',
                        'dueDate': timezone.now(),
                        'remindTime': 10}
        testToDo = toDoForm(data=form_data)
        self.assertFalse(testToDo.is_valid())

    def test_past_todo(self):
        """
        Todo with dueDate in the past is not displayed
        """
        form_data = {'title': 'testCase',
                     'content': 'test',
                     'dueDate': timezone.now() - datetime.timedelta(days=30),
                     'remindTime': 10}
        testToDo = toDoForm(data=form_data)
        self.assertFalse(testToDo.is_valid())

        self.assertEqual(testToDo.cleaned_data.get('title'), "testCase")
        self.assertEqual(testToDo.cleaned_data.get('content'), "test")
        # self.assertAlmostEqual(testToDo.cleaned_data.get('dueDate'), timezone.now()-datetime.timedelta(days=30), delta=datetime.timedelta(seconds=1))
        # fix later - cannot create ToDo w/dueDate < 10min in the future

    def test_future_todo(self):
        """
        Todo with dueDate in the future is displayed
        """
        form_data = {'title': 'testCase',
                     'content': 'test',
                     'dueDate': timezone.now() + datetime.timedelta(days=30),
                     'remindTime': 10}
        testToDo = toDoForm(data=form_data)
        self.assertTrue(testToDo.is_valid())

        self.assertEqual(testToDo.cleaned_data.get('title'), "testCase")
        self.assertEqual(testToDo.cleaned_data.get('content'), "test")
        self.assertAlmostEqual(testToDo.cleaned_data.get('dueDate'), timezone.now() + datetime.timedelta(days=30), delta=datetime.timedelta(seconds=1))


class CalendarTests(TestCase):
    def setUp(self):
        userModel = get_user_model()
        user = userModel.objects.create_user(username='testLogin', password='password')
        user.save()

    def test_CalendarCreate(self):
        """
        Calendar with valid data is displayed
        """
        today = timezone.now()
        year = today.year
        month = today.month
        user = User.objects.get(username='testLogin')
        try:
            Calendar(year, month, user).formatmonth(withyear=True)
            pass
        except:
            self.fail("invalid data")

    def test_CalendarCreateYearFail(self):
        """
        Calendar with invalid year data is not displayed
        """
        year = 20223    # year out of range
        month = 1
        user = User.objects.get(username='testLogin')
        try:
            Calendar(year, month, user).formatmonth(withyear=True)
            self.fail("incorrectly formatted calendar")
        except:
            pass

    def test_CalendarCreateMonthFail(self):
        """
        Calendar with invalid month data is not displayed
        """
        today = timezone.now()
        year = today.year
        month = 0       # invalid month
        user = User.objects.get(username='testLogin')
        try:
            Calendar(year, month, user).formatmonth(withyear=True)
            self.fail("incorrectly formatted calendar")
        except:
            pass