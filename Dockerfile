FROM python:3.14

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/prod.txt

# Install npm dependencies and build
WORKDIR /app/frontend
RUN npm install && npm run build

# Back to app root
WORKDIR /app
# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8080

# Note: Migrations run at startup, not build time
CMD python manage.py migrate --noinput && \
    gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --log-level info