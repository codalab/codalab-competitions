# Setup

## On *nix

1. git clone <whatever>
1. cd codalab-competitions
1. `cp .env_sample .env`

Open `.env` in your preferred editor

```
# ----------------------------------------------------------------------------
# Submission processing
# ----------------------------------------------------------------------------
SUBMISSION_TEMP_DIR=/tmp/codalab


# ----------------------------------------------------------------------------
# Storage
# ----------------------------------------------------------------------------

# Uncomment to use AWS
DEFAULT_FILE_STORAGE=storages.backends.s3boto.S3BotoStorage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=public
AWS_STORAGE_PRIVATE_BUCKET_NAME=private
AWS_S3_CALLING_FORMAT=boto.s3.connection.OrdinaryCallingFormat
AWS_S3_HOST=s3-us-west-2.amazonaws.com
AWS_QUERYSTRING_AUTH=False

# Uncomment to use Azure
DEFAULT_FILE_STORAGE=codalab.azure_storage.AzureStorage
AZURE_ACCOUNT_NAME=
AZURE_ACCOUNT_KEY=
AZURE_CONTAINER=public
# Only set these if bundle storage key is different from normal account keys
# BUNDLE_AZURE_ACCOUNT_NAME=
# BUNDLE_AZURE_ACCOUNT_KEY=
BUNDLE_AZURE_CONTAINER=bundles

# ----------------------------------------------------------------------------
# Database
# ----------------------------------------------------------------------------
MYSQL_ROOT_PASSWORD=mysql
MYSQL_DATABASE=codalab_website


# ----------------------------------------------------------------------------
# Caching
# ----------------------------------------------------------------------------
MEMCACHED_PORT=11211


# ----------------------------------------------------------------------------
# RabbitMQ and management
# ----------------------------------------------------------------------------
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
RABBITMQ_PORT=5671
RABBITMQ_HOST=rabbit
RABBITMQ_MANAGEMENT_PORT=15672
FLOWER_BASIC_AUTH=root:password
FLOWER_PORT=5555
FLOWER_CERTFILE=
FLOWER_KEYFILE=


# ----------------------------------------------------------------------------
# Django/nginx
# ----------------------------------------------------------------------------
NGINX_PORT=80
DJANGO_PORT=8000
SSL_PORT=443
SSL_CERTIFICATE=
SSL_CERTIFICATE_KEY=
# Allowed hosts separated by space
SSL_ALLOWED_HOSTS=


# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------
# Make sure LOG_DIR doesn't end with a slash
LOG_DIR=./logs
DJANGO_LOG_LEVEL=debug

```

From here, you may enter in any relevant information pertaining to your project. A few things that must be decided are:

1. Whether you will use AWS or Azure for storage
2. SSL Certs and their locations
3. Where your log files will live

## Storage

Codalab gives you the option of using AWS or Azure as your storage of choice. Depending on vendor you use, you must comment out the one you 
are not using in the _.env_ file.

### Create S3 storage containers (aws users only).

You may sign up for an AWS account [here](https://aws.amazon.com/s3/)

1. Sign into the AWS Management Console and open the Amazon S3 console at [here](https://console.aws.amazon.com/s3.)
1. Click **Create Bucket**
1. In the **Create a Bucket** dialog box, in the **Bucket Name** box, enter a bucket name
1. In the **Region** box, select a region.
1. Click **Create**

### Create AZURE storage containers (azure users only).

You may sign up for an Azure account [here](https://azure.microsoft.com/en-us/), then follow the directions below.

1. Log on to the [Azure Portal](https://portal.azure.com).
1. In the left pane, click **Storage**.
1. Select your storage account.
1. At the bottom of the dashboard, click **Manage Access Keys**. Copy your access keys, you'll need them later.
1. At the top of the dashboard page, click **Containers**.
1. At the bottom of the Containers page click **Add**.
1. Create a new container named "bundles". Set the **Access** to "Private".
1. Add another container named "public". Set the **Access** to "Public Blob".

## SSL Certification

Codalab allows you to set up SSL Certification for Nginx and RabbitMQ out of the box. Simply place your certs in the `/certs` dir of the project
root, then point `SSL_CERTIFICATE` and `SSL_CERTIFICATE_KEY` to the correct files respectively.

If you are curious about how to generate SSL certificates, you may glean some information [here]() and [here]()

## Log files

If you use codalab out of the box, you'll notice that we have supplied a persistent logs setup via docker volumes. This maps `LOG_DIR` to _/logs_
in the root of the project directory automatically, however, can be modified in your copy of `_.env_`

## Service Bus

Codalab uses task queue named Celery, and a message broker named RabbitMQ to handle external requests for the execution of **competition creations**, **submissions**, and other site related tasks.
This allows codalab to operate in a non-blocking way, essentially off loading HUGE tasks onto Celery, and polling it later for the results

### RabbitMQ How To

Codalab sets up an instance of RabbitMQ for you with default settings out of the box. If this does not work for you, you may 
change the `RABBITMQ_DEFAULT_USER` `RABBITMQ_DEFAULT_PASS` `RABBITMQ_PORT` `RABBITMQ_MANAGEMENT_PORT` envs in your local _.env_ file to better suit your setup.

You must alter codalabs RabbitMQ setup to require SSL be used in communication by setting the `SSL_CERTIFICATE` and `SSL_CERTIFICATE_KEY` in your local copy of `.env`

RabbitMQ starts with docker (See docker startup). Once this has finished, you must `docker exec -it rabbit bash` into your rabbit container, and 
enter `rabbitmq-plugins enable rabbitmq_management` in order to enable the **RabbitMQ Admin Panel**.

### Celery How To

Codalab uses 2 different "celery workers" to administer the tasks relating to their specification. These 2 workers are named **site-worker** and **compute-worker**.

Taking a quick look at /docker/run_compute.sh, we can see how celery works.

`celery -A codalab worker -l info -Q compute-worker -n compute-worker --concurrency=1 -Ofast -Ofair`

In this command above, `-A codalab worker` is attaching to our defined application _codalab_ and running the worker process.

`-l info` simply refers to the log level of the worker to be at "info".

Next option `-Q compute-worker`, tells our worker which queues to enable so it may pass messages across.

The option `-n compute-worker` gives our worker a common name. 

`--concurrency=1` tells celery how many child processes should process the queue; by default it equals the cores on your machine, however, we have set to _1_.

`-Ofast -Ofair` are optimizations to allow the worker to run smoother in a container.

**Knowing this information** can be helpful in times when tasks are not executing as expected. For that, we have included Flower Celery Monitor out of the box.

#### Flower

Flower is a Celery Monitoring tool that allows you view things such as: memory usage, tasks exchanges, and the state of any task ran through RabbitMQ.
This can be extremely helpful in troubleshooting any load balancing issues you may have by running tons of tasks.

To set this up, simply set the `FLOWER_BASIC_AUTH` and `FLOWER_PORT` in your local _.env_ file to match your desired setup.

To view the screenshots of what flower can monitor, visit the page [here](http://flower.readthedocs.io/en/latest/screenshots.html)

## Nginx How To

Codalab uses Nginx as the entrypoint to the project from the outside world. Nginx accomplishes this by listening to the `NGINX_PORT` and proxying
requests into the `django` host on `DJANGO_PORT`. You may set the values for `NGINX_PORT` and `DJANGO_PORT` in your local copy of `.env`, however
django is a hostname that is set in `docker-compose.yml` in order to register its dynamic IP into other services, such as `nginx` and `django`. If you wish
to change this hostname, you must change it everywhere else it is called as well.

If you would like to handle outside communication via SSL, codalab comes with a setup for that. Out of the box, codalab sets `SSL_PORT` to 443
in your copied version of `.env` and provides you with `./docker/nginx/ssl.conf`. 

You must configure `.env` to point to your own `SSL_CERTIFICATE` and `SSL_CERTIFICATE_KEY` in order for `ssl.conf` to work correctly
