release: python manage.py migrate && python manage.py collectstatic --noinput

web: gunicorn django_template.wsgi
worker: celery -A django_template worker --loglevel=info