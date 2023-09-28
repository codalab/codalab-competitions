FROM rabbitmq:management

RUN apt-get update && apt-get install -y gettext
# set consumer_timeout to > 27 hours
RUN echo "consumer_timeout=100000000" >> /etc/rabbitmq/conf.d/10-defaults.conf
