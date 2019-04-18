FROM ubuntu:18.04 as common

RUN apt-get update --fix-missing \
  && apt-get install -y wget git

COPY .git .git

ARG lumavate_exceptions_branch=master
ARG lumavate_signer_branch=master
ARG lumavate_token_branch=master
ARG lumavate_request_branch=master
ARG lumavate_properties_branch=master
ARG lumavate_service_util_branch=develop
ARG lumavate_editor_branch=master

RUN apt-get update && apt-get install -y git \
  && mkdir /python_packages \
  && cd /python_packages \
  && git clone https://github.com/LabelNexus/python-exceptions.git lumavate_exceptions \
  && git checkout $lumavate_exceptions_branch \
  && rm -rf /python_packages/lumavate_exceptions/.git \
  && git clone https://github.com/Lumavate-Team/python-signer.git lumavate_signer \
  && git checkout $lumavate_signer_branch \
  && rm -rf /python_packages/lumavate_signer/.git \
  && git clone https://github.com/LabelNexus/python-token.git lumavate_token \
  && git checkout $lumavate_token_branch \
  && rm -rf /python_packages/lumavate_token/.git \
  && git clone https://github.com/LabelNexus/python-api-request.git lumavate_request \
  && git checkout $lumavate_request_branch \
  && rm -rf /python_packages/lumavate_request/.git \
  && git clone https://github.com/LabelNexus/python-widget-properties.git lumavate_properties \
  && git checkout $lumavate_properties_branch \
  && rm -rf /python_packages/lumavate_properties/.git \
  && git clone https://github.com/Lumavate-Team/python-service-util.git lumavate_service_util \
  && cd lumavate_service_util \
  && git checkout $lumavate_service_util_branch \
  && cd ../ \
  && rm -rf /python_packages/lumavate_service_util/.git

FROM python:3.7.0-alpine

# Editor port
EXPOSE 5001

# App port
EXPOSE 5000

COPY --from=common /python_packages ./python_packages/
COPY requirements.txt ./

RUN apk add --no-cache \
    postgresql-libs \
  && apk add --no-cache --virtual .build-deps \
    gcc \
    git \
    libc-dev \
    libgcc \
    linux-headers \
    libffi-dev \
    libressl-dev \
    curl \
    musl-dev \
    postgresql-dev \
  && pip3 install -r requirements.txt \
  && rm -rf .git \
  && mkdir -p /app \
  && apk del .build-deps


# Editor code
RUN mkdir -p /editor
COPY ./editor /editor

# App code
RUN mkdir -p /app
COPY ./app /app

ENV APP_SETTINGS config/staging.cfg
ENV EDITOR_SETTINGS config/python_app.cfg
ENV PYTHONPATH /python_packages

# Supervisor base configuration
COPY supervisord.conf /etc/

# Dir for supervisor child configs
#RUN mkdir -p /etc/supervisor/conf.d

# Dir for supervisor & child logs
RUN mkdir -p /logs

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
