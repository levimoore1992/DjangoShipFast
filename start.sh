#!/bin/bash

# Run migrations
python manage.py migrate --noinput

# Start gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --log-level info