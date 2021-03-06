FROM python:3.7-alpine3.9

# Editor port
EXPOSE 5001

COPY edit_requirements.txt ./

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    libgcc \
    linux-headers \
    libffi-dev \
    libressl-dev \
    musl-dev \
  && pip3 install -r edit_requirements.txt \
  && mkdir -p /editor \
  && apk del .build-deps


# Editor code
COPY ./editor /editor

# Supervisor base configuration
COPY supervisord.conf /etc/supervisor/

# Dir for supervisor child configs
RUN mkdir -p /etc/supervisor/conf.d

# Dir for supervisor & child logs
RUN mkdir -p /logs

# Defualt command to start supervisor
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
