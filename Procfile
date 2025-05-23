release: python manage.py migrate && python manage.py collectstatic --noinput

web: gunicorn core.wsgi
worker: python manage.py procrastinate worker