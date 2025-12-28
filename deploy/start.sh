#!/bin/bash

echo "Running migrations..."
python manage.py migrate --noinput

if [ $? -ne 0 ]; then
  echo "Migration failed!"
  exit 1
fi

echo "Migrations completed successfully"

echo "Starting gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8080 --log-level debug