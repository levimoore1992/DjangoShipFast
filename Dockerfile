FROM python:3.14


WORKDIR /app

# Copy everything
COPY . .


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/prod.txt

# Back to app root
WORKDIR /app

EXPOSE 8080
