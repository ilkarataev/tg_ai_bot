FROM python:alpine3.18
WORKDIR /app
COPY requirements.txt ./
RUN apk update && apk add --no-cache mariadb-client build-base && \
    # pip install --upgrade pip setuptools && \
	pip install --no-cache-dir -r requirements.txt dataclasses && \
	# pip install --no-cache-dir  &&\
	rm -rf /tmp/* /var/tmp/*
COPY ./libs/ ./libs
COPY ./backend.py ./
COPY ./docker/backend/entrypoint.sh /entrypoint.sh
# RUN chmod +x docker/python/startup.sh
# ENTRYPOINT [ "sleep", "9999"]
ENTRYPOINT [ "/bin/sh", "/entrypoint.sh"]