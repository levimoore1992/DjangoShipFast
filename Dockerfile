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

# Make startup script executable
RUN chmod +x /app/deploy/start.sh

# Run collectstatic during build
RUN python manage.py collectstatic --noinput

# Use ENTRYPOINT instead of CMD - harder for platforms to override
ENTRYPOINT ["/app/deploy/start.sh"]