#!/bin/sh

su -m myuser -c "celery flower --broker=pyamqp://admin:rabbitmq@rabbit:5762//"