release: python manage.py migrate
web: gunicorn project.wsgi
worker: celery -A project.celery worker --pool=solo -l info