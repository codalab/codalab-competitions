#!/bin/sh

echo "GENERATING NGINX CONF TEMPLATE..."

# NOTE: We set dollar here to escape $var's in nginxconf, instead we write
# ${DOLLAR}var to escape it.
DOLLAR='$' envsubst < app/nginx/confs/nginx.conf > /etc/nginx/conf.d/default.conf

echo "COMPLETED:"

echo | cat /etc/nginx/conf.d/default.conf


nginx -g "daemon off;"