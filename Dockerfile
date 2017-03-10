FROM python:2.7
#COPY codalab/ /app
WORKDIR /app/codalab

RUN apt-get update && apt-get install -y npm python-mysqldb netcat

RUN easy_install MySQL-python
RUN pip install -r requirements/common.txt
RUN python manage.py collectstatic --noinput

RUN npm install .
RUN npm run build-css

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser 
