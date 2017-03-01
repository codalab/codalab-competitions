#!/bin/sh

# wait for MYSQL server to start

until netcat -z -v -w30 db 3306
do
  echo "Waiting for database connection..."
  # wait for 5 seconds before check again
  sleep 5
done

echo "WEB IS RUNNING"

cd codalab
python manage.py validate
# migrate db, so we have the latest db schema
python manage.py syncdb --migrate
# Insert initial data into the database
python scripts/initialize.py
# start development server on public ip interface, on port 8000
python manage.py runserver 0.0.0.0:8000