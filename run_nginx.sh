#!/bin/sh

echo | env

echo "@@@@@@@@@@@@@"
echo "${SSL_CERTIFICATE}"
echo $(-z "$SSL_CERTIFICATE")
echo "@@@@@@@@@@@@@"

echo "GENERATING NGINX CONF TEMPLATE..."

# NOTE: We set dollar here to escape $var's in nginxconf, instead we write
# ${DOLLAR}var to escape it.
export DOLLAR='$'

envsubst < app/nginx/confs/nginx.conf > /etc/nginx/conf.d/default.conf
echo "nginx/default.conf:"
echo | cat /etc/nginx/conf.d/default.conf

# Same thing if we're using SSL
if [[ $SSL_CERTIFICATE ]]
then
    echo "Using SSL certificate '${SSL_CERTIFICATE}' and allowing hosts '${SSL_ALLOWED_HOSTS}'"
    envsubst < app/nginx/confs/ssl.conf > /etc/nginx/conf.d/ssl.conf
    echo "nginx/ssl.conf:"
    echo | cat /etc/nginx/conf.d/ssl.conf
else
    echo "No SSL certificate env var (SSL_CERTIFICATE) found"
fi

nginx -g "daemon off;"
