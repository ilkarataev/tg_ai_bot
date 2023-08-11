FROM python:alpine3.18

WORKDIR /app

COPY requirements.txt ./
RUN apk update && apk add --no-cache mariadb-client build-base && \
	pip install -r requirements.txt && \
	pip install dataclasses && \
	rm -rf /tmp/* /var/tmp/*
COPY ./libs/ ./libs
COPY ./bot.py ./
COPY ./docker ./docker
RUN chmod +x docker/bot/startup.sh
ENTRYPOINT ["/bin/sh","docker/bot/startup.sh"]