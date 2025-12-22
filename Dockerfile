# ---------- Frontend build ----------
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# ---------- Backend ----------
FROM python:3.14

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . .

# Built assets already live in static/vite
COPY --from=frontend-builder /frontend/../static /app/static
    