FROM python:3.7

ARG USERNAME
ARG PASSWORD

ADD . /traces
WORKDIR /traces

RUN echo "machine nexus.mobilityservices.io login ${USERNAME} password ${PASSWORD}" > ~/.netrc
RUN pip install pipenv
RUN pipenv install --system --deploy --sequential
