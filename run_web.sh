#!/bin/sh

# wait for MYSQL server to start
sleep 10

mkdir -p /tmp/codalab
chmod ugo+rwx /tmp/codalab

# mkdir -p /tmp/python-eggs
# export PYTHON_EGG_CACHE=/tmp/python-eggs

cd codalab
python manage.py validate
# migrate db, so we have the latest db schema
python manage.py syncdb --migrate 
# Insert initial data into the database
python scripts/initialize.py
# start development server on public ip interface, on port 8000
python manage.py runserver 0.0.0.0:8000