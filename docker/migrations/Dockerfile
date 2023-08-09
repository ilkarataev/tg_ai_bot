FROM python:alpine3.18
WORKDIR /app
RUN apk update && apk add mariadb-client build-base
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./ /app
COPY ./docker/migrations/entrypoint.sh /entrypoint.sh
CMD ["/bin/sh", "/entrypoint.sh"]