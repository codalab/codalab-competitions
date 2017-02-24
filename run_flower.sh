#!/bin/sh

celery flower --broker=pyamqp://admin:rabbitmq@rabbit:5762//