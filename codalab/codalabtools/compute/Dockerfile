FROM python:2.7
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["worker.py"]


