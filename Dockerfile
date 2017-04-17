FROM python:2.7

RUN apt-get update && apt-get install -y npm python-mysqldb netcat nodejs-legacy

RUN easy_install MySQL-python
RUN pip install --upgrade pip  # make things faster, hopefully

COPY codalab/requirements/common.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/codalab
