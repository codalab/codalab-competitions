FROM python:2.7

# Copy this just to install quickly, copy rest of files later
COPY codalab/requirements/common.txt requirements.txt

RUN apt-get update && apt-get install -y npm python-mysqldb netcat nodejs-legacy

RUN easy_install MySQL-python
RUN pip install --upgrade pip  # make things faster, hopefully
RUN pip install -r requirements.txt

#VOLUME /app/codalab
COPY codalab/ /app

WORKDIR /app

#RUN find / -name manage.py

RUN python manage.py collectstatic --noinput

RUN npm install .
RUN npm run build-css

# create unprivileged user
RUN adduser --disabled-password --gecos '' workeruser
