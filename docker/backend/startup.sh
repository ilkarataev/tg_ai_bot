#!/bin/sh
while ! mysqladmin ping -s -h${DATABASE_HOST_MIGRATIONS}; 
do
  sleep 3
  echo "wait mysql"
done

# python backend.py