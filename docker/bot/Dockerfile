FROM python:alpine3.18

WORKDIR /app
COPY ./docker/bot/requirements.txt ./
RUN apk update && apk add --no-cache mariadb-client build-base && \
	pip install --no-cache-dir -r  requirements.txt && \
	# pip install dataclasses && \
	rm -rf /tmp/* /var/tmp/*
COPY ./libs/ ./libs
COPY ./bot.py ./
COPY ./docker/bot/startup.sh ./
ENTRYPOINT ["/bin/sh","startup.sh"]