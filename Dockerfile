FROM python:3.11.9-alpine3.18

COPY requirements.txt /tmp/
# git sqlite3 libpq-dev libpq5 gcc g++
RUN apk update && apk add bash
RUN apk add gcc g++
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /wiki
COPY src/ /wiki/src/
COPY settings/ /wiki/settings/
COPY alembic/ /wiki/alembic/
COPY main.py alembic.ini /wiki/
# COPY tests/ /tests/

WORKDIR /wiki

EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=5s --retries=5 --start-period=5s CMD curl -f 0.0.0.0:8080/healthcheck || exit 1
# CMD python main.py
