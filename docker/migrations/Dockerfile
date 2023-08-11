FROM python:alpine3.18
WORKDIR /app
RUN apk update && apk add --no-cache mariadb-client build-base
COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt
COPY ./ /app
COPY ./docker/migrations/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]