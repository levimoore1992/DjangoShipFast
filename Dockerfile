FROM python:3.14


WORKDIR /app

# Copy everything
COPY . .


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/prod.txt

# Back to app root
WORKDIR /app
# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8080

# Note: Migrations run at startup, not build time
CMD python manage.py migrate --noinput && \
    gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --log-level info