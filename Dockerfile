FROM python:3.10

# Next line is needed for restore_db command
RUN apt-get update && apt-get install -y postgresql-client

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
COPY . /app/
WORKDIR /app

# Install any needed packages specified in requirements.txt as well as uwsgi
RUN pip install -r requirements/dev.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000
