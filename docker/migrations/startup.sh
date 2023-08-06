#!/bin/sh

while ! mysqladmin ping -h${DATABASE_HOST_MIGRATIONS} --silent; do
  sleep 1
done

alembic upgrade head