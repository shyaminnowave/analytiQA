FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # Additional dependencies
  && apt-get install -y git \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . .

# Accept and set build-time environment variables from GitHub Actions
ARG SECRET_KEY
ARG ALLOWED_HOSTS
ARG CELERY_BROKER_URL
ARG CELERY_RESULT_BACKEND
ARG CORS_ALLOWED_ORIGINS
ARG CORS_ALLOW_CREDENTIALS
ARG CORS_ORIGIN_ALLOW_ALL
ARG DATABASE_ENGINE
ARG DEBUG
ARG EMAIL_HOST
ARG EMAIL_HOST_USER
ARG EMAIL_HOST_PASSWORD
ARG HOST
ARG INTERNAL_IPS
ARG NAME
ARG PASSWORD
ARG PORT
ARG USER

ENV SECRET_KEY=${SECRET_KEY}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV CELERY_BROKER_URL=${CELERY_BROKER_URL}
ENV CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
ENV CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
ENV CORS_ALLOW_CREDENTIALS=${CORS_ALLOW_CREDENTIALS}
ENV CORS_ORIGIN_ALLOW_ALL=${CORS_ORIGIN_ALLOW_ALL}
ENV DATABASE_ENGINE=${DATABASE_ENGINE}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DEBUG=${DEBUG}
ENV EMAIL_HOST=${EMAIL_HOST}
ENV EMAIL_HOST_USER=${EMAIL_HOST_USER}
ENV EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
ENV HOST=${HOST}
ENV INTERNAL_IPS=${INTERNAL_IPS}
ENV NAME=${NAME}
ENV PASSWORD=${PASSWORD}
ENV PORT=${PORT}
ENV USER=${USER}


RUN python manage.py migrate
RUN python manage.py runserver

EXPOSE 8000