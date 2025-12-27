FROM python:3.14

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements/prod.txt
RUN npm install

COPY . .

# Build Vite assets
RUN npm run build

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]