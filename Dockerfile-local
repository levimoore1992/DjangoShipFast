FROM python:3.12

#################################
# For the restore db command
#################################
 #Add PostgreSQL 16 repository for Debian
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# Install PostgreSQL 16 client
RUN apt-get update && \
    apt-get install -y postgresql-client-16 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
#################################
#################################

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
COPY . /app/
WORKDIR /app

# Install any needed packages specified in requirements.txt as well as uwsgi
RUN pip install --upgrade pip && \
    pip install -r requirements/dev.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000
