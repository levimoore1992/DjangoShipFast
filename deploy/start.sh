#!/bin/bash

echo "Running migrations..."
python manage.py migrate --noinput

if [ $? -ne 0 ]; then
  echo "Migration failed!"
  exit 1
fi

echo "Migrations completed successfully"

# Keep the default modest; deployments can tune WORKERS to their memory and load.
WORKERS=${WORKERS:-2}
TIMEOUT=${GUNICORN_TIMEOUT:-120}
LOG_LEVEL=${GUNICORN_LOG_LEVEL:-info}

echo "Starting gunicorn with $WORKERS workers, timeout $TIMEOUT, log level $LOG_LEVEL..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --log-level "$LOG_LEVEL"