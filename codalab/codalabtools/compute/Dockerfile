FROM continuumio/anaconda:4.3.0
RUN mkdir -p /app
COPY . /app
WORKDIR /app/codalab/codalabtools/compute
RUN apt-get install -y build-essential && \
    apt-get install -y psmisc && \
    pip install -r requirements.txt && \
    mkdir /tmp/codalab && \
    chmod -R ugo+rwx /tmp/codalab
    

#RUN mkdir codalabtools
#RUN wget -O codalabtools.py https://raw.githubusercontent.com/jared-cain/codalab-competitions/jared-dev/codalab/codalabtools/__init__.py && \
#    wget https://raw.githubusercontent.com/jared-cain/codalab-competitions/jared-dev/codalab/codalabtools/azure_extensions.py
ENTRYPOINT ["python"]
CMD ["worker.py"]




