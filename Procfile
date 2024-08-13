release: python manage.py migrate && python manage.py collectstatic --noinput

web: gunicorn django_template.wsgi
worker: celery -A tech_guru worker --loglevel=info