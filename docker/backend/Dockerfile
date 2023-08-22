FROM python:alpine3.18
WORKDIR /app
COPY ./docker/backend/requirements.txt ./
RUN apk update && apk add --no-cache mariadb-client build-base && \
    # pip install --upgrade pip setuptools && \
	pip install --no-cache-dir -r requirements.txt && \
	# pip install --no-cache-dir dataclasses &&\
	rm -rf /tmp/* /var/tmp/*
COPY ./libs/ ./libs
COPY ./*.py ./
COPY ./docker/backend/entrypoint.sh /entrypoint.sh
# RUN chmod +x docker/python/startup.sh
ENTRYPOINT [ "/bin/sh", "/entrypoint.sh"]