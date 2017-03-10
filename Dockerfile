FROM python:2.7
COPY . /app

WORKDIR /app/codalab

RUN apt-get update && apt-get install -y npm python-mysqldb netcat nodejs-legacy

RUN easy_install MySQL-python
RUN pip install --upgrade pip  # make things faster, hopefully
RUN pip install -r requirements/common.txt
RUN python manage.py collectstatic --noinput

RUN npm install .
RUN npm run build-css

WORKDIR /app

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser 
