FROM python:3.14

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    DJANGO_SETTINGS_MODULE=core.settings

# Install dependencies
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy project files
COPY . /app/

# Create a startup script that ensures migrations run
RUN echo '#!/bin/bash\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
if [ $? -ne 0 ]; then\n\
  echo "Migration failed!"\n\
  exit 1\n\
fi\n\
echo "Migrations completed successfully"\n\
\n\
echo "Starting gunicorn..."\n\
exec gunicorn core.wsgi:application --bind 0.0.0.0:8080 --log-level debug\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Already run collectstatic during build
RUN python manage.py collectstatic --noinput

# Use ENTRYPOINT instead of CMD - harder for platforms to override
ENTRYPOINT ["/app/start.sh"]