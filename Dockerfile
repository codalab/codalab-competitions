FROM --platform=linux/amd64 python:3.8-bookworm

# For nodejs
RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -
RUN apt-get update && apt-get install -y npm netcat nodejs python3-dev libmemcached-dev

# Force pip 23.3.1, compatible with celery 4.4.6
RUN python -m pip install --no-cache-dir "pip==23.3.1"
COPY codalab/requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/codalab
