FROM continuumio/anaconda:4.3.0

RUN apt-get update && apt-get install -y build-essential psmisc

# Copy this just to install quickly, copy rest of files later
COPY codalab/requirements/compute_worker.txt requirements.txt
RUN pip install -r requirements.txt

#COPY codalab/ /app/codalab

WORKDIR /app/codalab

ENV PYTHONPATH $PYTHONPATH:/app:/app/codalab:/app/apps

# create unprivileged user
RUN adduser --disabled-password --gecos '' workeruser

USER workeruser
CMD celery -A codalab worker -l info -Q compute-worker -n compute-worker -Ofast -Ofair --logfile=/var/log/compute_worker.log --concurrency=1
