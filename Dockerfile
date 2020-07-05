FROM python:3.7

ARG USERNAME
ARG PASSWORD

ADD locintel /locintel
WORKDIR /locintel

RUN pip install poetry
RUN poetry install --no-root
