FROM python:2.7
COPY codalab/ /app

WORKDIR /app
#VOLUME /app/codalab

RUN apt-get update && apt-get install -y npm python-mysqldb netcat nodejs-legacy

RUN easy_install MySQL-python
RUN pip install --upgrade pip  # make things faster, hopefully
RUN pip install -r requirements/common.txt
RUN python manage.py collectstatic --noinput

RUN npm install .
RUN ls apps/web/static/less/ && npm run build-css

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser 
