FROM python:3.6-alpine

RUN apk -U upgrade && apk add build-base postgresql-dev

WORKDIR /app
ADD . /app/
RUN pip install -e .[dev]
