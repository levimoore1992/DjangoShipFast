# ---------- Frontend build stage ----------
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# ---------- Backend runtime stage ----------
FROM python:3.14

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy Django project
COPY . .

# Copy built frontend assets into Django static directory
COPY --from=frontend-builder /frontend/dist /app/static/vite

    