#!/usr/bin/env bash
while ! mysqladmin ping -s -h${DATABASE_HOST_MIGRATIONS}; 
do
   sleep 3
   echo "waiting for mysql ..."
done
alembic upgrade head