FROM ubuntu:18.04

RUN apt-get update --fix-missing \
  && apt-get install -y wget git \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get install -y libpq-dev --fix-missing
RUN apt-get install -y libffi-dev

COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt

COPY .git .git

ARG lumavate_exceptions_branch=master
ARG lumavate_signer_branch=master
ARG lumavate_token_branch=master
ARG lumavate_request_branch=master
ARG lumavate_properties_branch=master
ARG lumavate_service_util_branch=master
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
  && git checkout $lumavate_service_util_branch \
  && rm -rf /python_packages/lumavate_service_util/.git


# Install python 2 to run supervisor
RUN mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/

RUN apt-get install python2.7 python-pip -y && \
    pip install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip2 install supervisor

# Editor port
EXPOSE 5001

# Editor code
RUN mkdir -p /editor

COPY ./app /editor

COPY ./signer_cli.py /signer_cli.py

ENV APP_SETTINGS config/staging.cfg
ENV PYTHONPATH /python_packages

#CMD ["supervisord", "-c", "/etc/supervisord.conf"]
