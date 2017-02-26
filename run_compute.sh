#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

cd codalab

mkdir -p /tmp/codalab
chmod ugo+rwx /tmp/codalab

# Start compute worker
celery -A codalab worker -l info -Q compute-worker -n compute-worker --concurrency=1 -Ofast -Ofair 