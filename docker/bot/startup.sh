#!/bin/sh

while ! mysqladmin ping -s -h${DATABASE_HOST_MIGRATIONS}; do
  sleep 1
done

python bot.py