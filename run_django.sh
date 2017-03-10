#!/bin/sh

echo "Waiting for database connection..."

until netcat -z -v -w30 mysql 3306
do
  sleep 1
done

cd codalab

echo "WEB IS RUNNING"

# migrate db, so we have the latest db schema
python manage.py syncdb --migrate

# Insert initial data into the database
python scripts/initialize.py

# start development server on public ip interface, on port 8000
gunicorn codalab.wsgi --bind django:$DJANGO_PORT
