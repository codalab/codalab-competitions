FROM continuumio/anaconda:4.3.0

RUN apt-get update && apt-get install -y build-essential psmisc

# Copy this just to install quickly, copy rest of files later
COPY codalab/requirements/compute_worker.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/codalab

ENV PYTHONPATH $PYTHONPATH:/app:/app/codalab:/app/apps

# Install docker, specific version
RUN curl -sSL https://get.docker.com/ | sed 's/docker-ce/docker-ce=17.06.0~ce-0~debian/' | sh

#USER workeruser
CMD celery -A codalab worker -l info -Q compute-worker -n compute-worker -Ofast -Ofair --concurrency=1
