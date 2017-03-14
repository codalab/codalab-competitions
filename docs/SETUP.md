# Setup

#### To run an entire instance of the Codalab website

You'll need to create a storage container (AWS S3 or Azure) and configure a `.env` file which will store your settings like: storage keys, SSL certificate paths and ports that are open.

#### To run a worker to process submissions

If you're just attaching to a queue go to the [run a compute worker](#run-a-compute-worker) section.

## On Mac/Linux

Clone the project and make a copy of `.env_sample` called `.env` in the root of the project directory.

1. Install docker ([mac](https://download.docker.com/mac/stable/Docker.dmg) or [Ubuntu](https://docs.docker.com/engine/installation/linux/ubuntu/#install-docker))
1. `git clone git@github.com:codalab/codalab-competitions.git`
1. `cd codalab-competitions`
1. `cp .env_sample .env`

## On Windows

*TODO describe how to install on Windows*

## Editing project variables

Open `.env` in your preferred editor

*TODO describe the non-obvious env vars and maybe special ones?*

```ini
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

# Storage

Codalab gives you the option of using AWS or Azure as your storage of choice. Depending on vendor you use, you must comment out the one you are not using in the `.env` file.

### AWS S3

Sign in or create an AWS account [here](https://aws.amazon.com/s3/) and then create a private and public bucket.

*TODO: Bucket Policies, CORS*

1. You don't have to do this if you've already setup Azure Blob Storage!
1. Sign into the AWS Management Console and open the Amazon S3 console at [here](https://console.aws.amazon.com/s3.)
1. Click **Create Bucket**
1. In the **Create a Bucket** dialog box, in the **Bucket Name** box, enter a bucket name
1. In the **Region** box, select a region.
1. Click **Create**

### Azure blob storage

You may sign up for an Azure account [here](https://azure.microsoft.com/en-us/), then follow the directions below.

1. You do not have to do this if you've already setup S3!
1. Log on to the [Azure Portal](https://portal.azure.com).
1. In the left pane, click **Storage**.
1. Select your storage account.
1. At the bottom of the dashboard, click **Manage Access Keys**. Copy your access keys, you'll need them later.
1. At the top of the dashboard page, click **Containers**.
1. At the bottom of the Containers page click **Add**.
1. Create a new container named "bundles". Set the **Access** to "Private".
1. Add another container named "public". Set the **Access** to "Public Blob".

*TODO What do you get from Azure and where do you put it in `.env`?*

# Run a compute worker

1. Install docker ([mac](https://download.docker.com/mac/stable/Docker.dmg) or [Ubuntu](https://docs.docker.com/engine/installation/linux/ubuntu/#install-docker))
1. `git clone git@github.com:codalab/codalab-competitions.git`
1. `cd codalab-competitions`
1. `cp .env_sample .env`

Edit `.env` and set your `BROKER_URL` from the worker management screen: <br> ![image](https://cloud.githubusercontent.com/assets/2185159/23891328/f3b62dd0-0852-11e7-8da4-12e5dd8a7383.png)

Now your configuration file should look something like this:

```
BROKER_URL=pyamqp://cd980e2d-78f9-4707-868d-bdfdd071...
```

Then you can run the worker:

```
$ docker-compose start worker_compute
```


# Logging

To change where logs are kept, modify `LOG_DIR` in your `.env` configuration file.

