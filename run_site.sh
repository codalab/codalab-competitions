#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

cd codalab

mkdir -p /tmp/codalab
chmod ugo+rwx /tmp/codalab

# Start site worker
celery -A codalab worker -l info -Q site-worker -n site-worker --concurrency=2 -Ofast -Ofair
