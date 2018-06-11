FROM python:2.7

RUN curl -sL https://deb.nodesource.com/setup_4.x | bash -

RUN apt-get update && apt-get install -y npm netcat nodejs

RUN pip install --upgrade pip  # make things faster, hopefully

COPY codalab/requirements/common.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/codalab
