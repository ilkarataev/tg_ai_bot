FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
# FROM ubuntu:22.04
WORKDIR /app
COPY ./requirements.txt ./
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y

RUN apt install software-properties-common git -y && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install python3.10 libpython3-dev python3-dev python3-tk \
    ffmpeg python3-pip -y && \
    pip install -r requirements.txt


RUN git clone https://github.com/s0md3v/roop.git Roop && \
    cd Roop && pip install -r requirements.txt && \
    pip install -U insightface
#  проблема с пакетом возможно нужна установка
COPY ./libs/ ./libs
COPY ./*.py ./
# COPY ./docker/backend/entrypoint.sh /entrypoint.sh
# # RUN chmod +x docker/python/startup.sh
# ENTRYPOINT [ "/bin/sh", "/entrypoint.sh"]


# docker build -t ilia_test -f docker/client/Dockerfile .

# docker run --rm -it ilia_test bash
