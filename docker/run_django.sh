#!/bin/sh

echo "Waiting for database connection..."

until netcat -z -v -w30 $DB_HOST $DB_PORT
do
  sleep 1
done

echo "WEB IS RUNNING"

# Static files
npm install .
npm run build-css
python manage.py collectstatic --noinput

# migrate db, so we have the latest db schema
python manage.py syncdb --migrate

# Insert initial data into the database
python scripts/initialize.py

# start development server on public ip interface, on port 8000
PYTHONUNBUFFERED=TRUE gunicorn codalab.wsgi --bind django:$DJANGO_PORT --access-logfile=/var/log/django/access.log --error-logfile=/var/log/django/error.log --log-level $DJANGO_LOG_LEVEL --reload --enable-stdio-inheritance
