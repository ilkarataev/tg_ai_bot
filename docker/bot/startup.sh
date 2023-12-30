#!/bin/sh

while ! mysqladmin ping -s -h${DATABASE_HOST}
do
  sleep 3
  echo "wait until mysql up"
done

exec python -u bot.py