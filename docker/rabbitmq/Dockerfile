FROM rabbitmq:3.6.16-management

RUN apt-get update && apt-get install -y gettext

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["rabbitmq-server"]
