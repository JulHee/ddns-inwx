FROM python:3.6-slim

ENV APP /app
RUN mkdir $APP
WORKDIR $APP

RUN apt-get update && apt-get install -y \
    gcc \
    libpcre3 \
    libpcre3-dev \
    g++

COPY requirements.txt .
RUN pip install requests
RUN pip install -r requirements.txt

RUN mkdir -p /etc/uwsgi/
COPY uwsgi/uwsgi.ini /etc/uwsgi/inwx.ini

COPY . /app
