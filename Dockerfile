FROM python:2.7
ADD ./codalab/requirements/common.txt /app/common.txt
WORKDIR /app
RUN easy_install MySQL-python
RUN apt-get update && apt-get install -y python-mysqldb
RUN pip install -r common.txt
# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser 
