FROM continuumio/anaconda:4.3.0
RUN mkdir -p /app
COPY . /app
WORKDIR /app/codalab/codalabtools/compute
RUN apt-get update && apt-get install -y \ 
    build-essential psmisc
RUN pip install -r requirements.txt
RUN mkdir /tmp/codalab
RUN chmod -R ugo+rwx /tmp/codalab
ENTRYPOINT ["python"]
CMD ["worker.py"]




