FROM python:3.12.0b4-alpine3.18

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update && apt-get upgrade -y && apt-get install -y mariadb-client
RUN pip install -r requirements.txt && \
		pip install dataclasses &&\
		rm -rf /tmp/* /var/tmp/*
COPY ./libs/ ./libs
COPY ./bot.py ./
COPY ./docker ./docker
RUN chmod +x docker/python/startup.sh
CMD ["docker/python/startup.sh"]