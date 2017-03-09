#!/bin/sh

echo "GENERATING NGINX CONF TEMPLATE..."

envsubst < app/nginx/confs/nginx.conf > /etc/nginx/conf.d/nginx.conf

echo "COMPLETED:"

echo | cat /etc/nginx/conf.d/nginx.conf
