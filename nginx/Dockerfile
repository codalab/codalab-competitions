FROM nginx
RUN rm /etc/nginx/conf.d/default.conf
#ADD confs/ /etc/nginx/conf.d/

RUN envsubst < app/nginx/confs/nginx.conf > /etc/nginx/conf.d/nginx.conf
RUN echo "Completed conf generation:"
RUN echo | cat /etc/nginx/conf.d/nginx.conf

# forward request logs to Docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE $NGINX_PORT 443

CMD ["nginx", "-g", "daemon off;"]
