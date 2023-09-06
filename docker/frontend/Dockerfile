FROM python:alpine3.18

WORKDIR /app
COPY ./docker/frontend/requirements.txt ./
RUN apk update && apk add --no-cache mariadb-client build-base && \
    pip install --upgrade pip && \
    pip install -r requirements.txt &&\
    rm -rf /tmp/* /var/tmp/*

COPY ./libs ./libs
COPY ./frontend/ ./frontend
COPY ./docker/frontend/entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/bin/sh", "/entrypoint.sh"]
