#!/bin/sh
while ! mysqladmin ping -s -h${DATABASE_HOST}
do
  sleep 3
  echo "wait mysql"
done
cd frontend/
exec python app.py