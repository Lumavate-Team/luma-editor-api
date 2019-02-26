FROM ubuntu:16.04 as common

RUN apt-get update --fix-missing \
    && apt-get install -y wget git

COPY keys keys
COPY .git .git
COPY git.sh ./

ARG lumavate_exceptions_branch=master
ARG lumavate_signer_branch=master
ARG lumavate_token_branch=master
ARG lumavate_request_branch=master
ARG lumavate_properties_branch=master
ARG lumavate_service_util_branch=master
ARG lumavate_editor_branch=master

RUN apt-get update && apt-get install -y git \
  && mkdir /root/.ssh/ \
  && touch /root/.ssh/known_hosts \
  && ssh-keyscan github.com >> /root/.ssh/known_hosts \
  && chmod 400 /keys/* \
  && mkdir /python_packages \
  && cd /python_packages \
  && /git.sh -i /keys/python-exceptions-rsa clone git@github.com:LabelNexus/python-exceptions.git lumavate_exceptions \
  && git checkout $lumavate_exceptions_branch \
  && rm -rf /python_packages/lumavate_exceptions/.git \
  && git clone https://github.com/Lumavate-Team/python-signer.git lumavate_signer \
  && git checkout $lumavate_signer_branch \
  && rm -rf /python_packages/lumavate_signer/.git \
  && /git.sh -i /keys/python-token-rsa clone git@github.com:LabelNexus/python-token.git lumavate_token \
  && git checkout $lumavate_token_branch \
  && rm -rf /python_packages/lumavate_token/.git \
  && /git.sh -i /keys/python-api-request-rsa clone git@github.com:LabelNexus/python-api-request.git lumavate_request \
  && git checkout $lumavate_request_branch \
  && rm -rf /python_packages/lumavate_request/.git \
  && /git.sh -i /keys/python-widget-properties-rsa clone git@github.com:LabelNexus/python-widget-properties.git lumavate_properties \
  && git checkout $lumavate_properties_branch \
  && rm -rf /python_packages/lumavate_properties/.git \
  && /git.sh -i /keys/python-service-util-rsa clone git@github.com:Lumavate-Team/python-service-util.git lumavate_service_util \
  && git checkout $lumavate_service_util_branch \
  && rm -rf /python_packages/lumavate_service_util/.git \
  && mkdir /lumavate_editor \
  && git clone git@github.com:Lumavate-Team/luma-editor-api.git lumavate_editor \
  && git checkout $lumavate_editor_branch

FROM python:3.7.0-alpine

EXPOSE 5000
EXPOSE 5001

COPY --from=common /python_packages ./python_packages/
COPY requirements.txt ./
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/

RUN apk add --no-cache python2 && \
    python2 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip2 install supervisor

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
  && mkdir -p /app-dev \
  && apk del .build-deps

ENV PYTHONPATH /python_packages
WORKDIR /app
COPY ./app /app
COPY ./app /app-dev
COPY ./signer_cli.py /signer_cli.py

ENV APP_SETTINGS config/staging.cfg

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
