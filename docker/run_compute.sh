#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

cd codalab

mkdir -p $SUBMISSION_TEMP_DIR
chmod ugo+rwx $SUBMISSION_TEMP_DIR

mkdir -p /tmp/python-eggs
export PYTHON_EGG_CACHE=/tmp/python-eggs
chmod ugo+rwx /tmp/python-eggs

touch ${LOG_DIR}/compute_worker.log

# Start compute worker
su -m workeruser -c "celery -A codalab worker -l info -Q compute-worker -n compute-worker -Ofast -Ofair --logfile=/var/log/compute_worker.log --concurrency=1"
 