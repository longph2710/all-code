FROM python:3.9-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update && apt-get -y --no-install-recommends install default-libmysqlclient-dev gcc
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/