ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-slim AS frontend-dependencies
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM frontend-dependencies AS frontend-development
CMD ["npm", "run", "dev"]

FROM frontend-dependencies AS frontend-builder
COPY frontend/ .
RUN npm run build
# Fix manifest location for Django-Vite compatibility (Vite 5+ puts it in .vite/)
RUN if [ -f /app/static/vite/.vite/manifest.json ]; then mv /app/static/vite/.vite/manifest.json /app/static/vite/manifest.json; fi

FROM python:3.14-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    DJANGO_SETTINGS_MODULE=core.settings

# psycopg requires the PostgreSQL runtime library.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy project files
COPY . /app/

# Copy frontend assets
COPY --from=frontend-builder /app/static/vite /app/static/vite

# Make startup script executable
RUN chmod +x /app/deploy/start.sh

# Run collectstatic during build
RUN python manage.py collectstatic --noinput

# Use ENTRYPOINT instead of CMD - harder for platforms to override
ENTRYPOINT ["/app/deploy/start.sh"]