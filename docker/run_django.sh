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

python manage.py migrate

# Use node to edit site domain from .env
node << EOF
//Read data
var data = require('./apps/web/fixtures/initial_data.json')  

//Manipulate data
data.forEach((v,i,a) =>{
  if (v.model === "sites.site"){
    console.log('Changing domain: ' + v.fields.domain + ' to ' + process.env.CODALAB_SITE_DOMAIN)
    v.fields.domain = process.env.CODALAB_SITE_DOMAIN
    v.fields.name = 'CODALAB_SITE_DOMAIN'
  }
})


//Output data
const fs = require('fs')
content = JSON.stringify(data)
fs.writeFile('./apps/web/fixtures/initial_data.json', content, err => {
  if (err) {
    console.error(err)
    return
  }
  //file written successfully
})

EOF

# For Django 1.7 we cannot run this here. Now using fixtures with loaddata, keeping this here for history
# Insert initial data into the database

python manage.py loaddata initial_data.json initial_team_data.json

# start development server on public ip interface, on port 8000
PYTHONUNBUFFERED=TRUE gunicorn codalab.wsgi \
    --bind django:$DJANGO_PORT \
    --access-logfile=/var/log/django/access.log \
    --error-logfile=/var/log/django/error.log \
    --log-level $DJANGO_LOG_LEVEL \
    --reload \
    --timeout 4096 \
    --enable-stdio-inheritance
