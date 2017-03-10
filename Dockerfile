FROM python:2.7
ADD . /app
WORKDIR /app/codalab

RUN apt-get update
RUN apt-get install -y npm python-mysqldb netcat

RUN npm install .

RUN easy_install MySQL-python
RUN pip install -r requirements/common.txt

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser 
