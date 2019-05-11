#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

# Start site worker
celery -A codalab worker -B -l debug -Q site-worker,submission-updates -n site-worker -Ofast -Ofair --concurrency=${SITE_WORKER_CONCURRENCY:-2} --config=codalab.celery
