FROM python:3.11.4-alpine3.18
WORKDIR /app
RUN apk update && apk add mariadb-client build-base
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./ /app
RUN chmod +x docker/migrations/startup.sh
CMD ["docker/migrations/startup.sh"]