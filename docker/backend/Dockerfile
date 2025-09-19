FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка русской локали
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y locales
RUN sed -i 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen
RUN locale-gen
ENV LANG ru_RU.UTF-8
RUN echo 'LANG=ru_RU.UTF-8' >> /etc/default/locale
RUN ln -sf /usr/share/zoneinfo/Asia/Yekaterinburg /etc/localtime
RUN echo "Asia/Yekaterinburg" > /etc/timezone

RUN apt-get install -y postgresql-client cron vim mc procps libpq-dev python3-requests make dos2unix
RUN apt-get install -y librabbitmq-dev libssh-dev libpq-dev
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY ./backend/.python-version .
COPY ./backend/pyproject.toml .
COPY ./backend/uv.lock .
RUN uv sync
COPY ./backend/src /app
ENV DJANGO_SETTINGS_MODULE=config.settings
