FROM python:alpine3.18
WORKDIR /app
RUN apk update && apk add --no-cache mariadb-client
COPY ./docker/migrations/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt
COPY ./alembic.ini ./alembic.ini
COPY ./libs/ ./libs
COPY ./migrations ./migrations
COPY ./docker/migrations/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]