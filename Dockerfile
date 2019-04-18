FROM python:3.7.0-alpine

# Editor port
EXPOSE 5001

COPY edit_requirements.txt ./

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    git \
    libc-dev \
    libgcc \
    linux-headers \
    libffi-dev \
    libressl-dev \
    curl \
    musl-dev \
  && pip3 install -r edit_requirements.txt \
  && rm -rf .git \
  && mkdir -p /editor \
  && apk del .build-deps


# Editor code
COPY ./editor /editor

ENV EDITOR_SETTINGS config/python_app.cfg

# Supervisor base configuration
COPY supervisord.conf /etc/

# Dir for supervisor child configs
RUN mkdir -p /etc/supervisor/conf.d

# Dir for supervisor & child logs
RUN mkdir -p /logs
