FROM python:2.7
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN wget -O codalabtools.py https://raw.githubusercontent.com/jared-cain/codalab-competitions/jared-dev/codalab/codalabtools/__init__.py && \
    wget https://raw.githubusercontent.com/jared-cain/codalab-competitions/jared-dev/codalab/codalabtools/azure_extensions.py
ENTRYPOINT ["python"]
CMD ["worker.py"]




