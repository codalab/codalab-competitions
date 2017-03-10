#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

cd codalab

mkdir -p /tmp/codalab
chmod ug+rwx /tmp/codalab

mkdir -p /tmp/python-eggs
export PYTHON_EGG_CACHE=/tmp/python-eggs
chmod ugo+rwx /tmp/python-eggs

# Start site worker
celery -A codalab worker -l info -Q site-worker,submission-updates -n site-worker --concurrency=2 -Ofast -Ofair
