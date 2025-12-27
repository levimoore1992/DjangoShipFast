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

EXPOSE 8080

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8080"]