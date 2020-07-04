FROM python:3.7

ARG USERNAME
ARG PASSWORD

ADD geotools /geotools
WORKDIR /geotools

RUN pip install poetry
RUN poetry install --no-root
