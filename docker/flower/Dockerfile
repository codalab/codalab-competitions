FROM totem/celery-flower-docker

# Edit the default docker image to take BROKER_USE_SSL
RUN echo "BROKER_USE_SSL = os.environ.get('BROKER_USE_SSL')" >> /opt/celery-flower/celeryconfig.py
