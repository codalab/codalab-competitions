#!/bin/sh

envsubst < app/nginx/confs/nginx.conf > /etc/nginx/conf.d/nginx.conf
