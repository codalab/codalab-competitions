#!/bin/sh

echo "Waiting for database connection..."

until netcat -z -v -w30 $DB_HOST $DB_PORT
do
  sleep 1
done

echo "WEB IS RUNNING"

# Static files
npm cache clean
npm install .
npm install -g less
npm run build-css
python manage.py collectstatic --noinput

# Syncdb is deperecated, replaced with migrate. Keeping this here for history.
# migrate db, so we have the latest db schema
#python manage.py syncdb --migrate

python manage.py migrate
python manage.py loaddata initial_data.json

# For Django 1.7 we cannot run this here. Now using fixtures above with loaddata, keeping this here for history
# Insert initial data into the database
#python scripts/initialize.py

# start development server on public ip interface, on port 8000
PYTHONUNBUFFERED=TRUE gunicorn codalab.wsgi \
    --bind django:$DJANGO_PORT \
    --access-logfile=/var/log/django/access.log \
    --error-logfile=/var/log/django/error.log \
    --log-level $DJANGO_LOG_LEVEL \
    --reload \
    --timeout 4096 \
    --enable-stdio-inheritance
