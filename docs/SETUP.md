# Setup

Make a copy of _.env\_sample_ called _.env_ in the root of the project directory.

From here, you may enter in any relevant information pertaining to your project. A few things that must be decided are:

1. Whether you will use AWS or Azure for storage
2. What your SSL certs will be named
3. Where your log files will live

## Storage

Codalab gives you the option of using AWS or Azure as your storage of choice. Depending on vendor you use, you must comment out the one you 
are not using in the _.env_ file.

You may sign up for an AWS account [here](https://aws.amazon.com/s3/)

<!--TODO: ADD AWS s3 directions-->

You may sign up for an Azure account [here](https://azure.microsoft.com/en-us/), then follow the directions below.

### Create AZURE storage containers (azure users only).

1. Log on to the [Azure Portal](https://portal.azure.com).
1. In the left pane, click **Storage**.
1. Select your storage account.
1. At the bottom of the dashboard, click **Manage Access Keys**. Copy your access keys, you'll need them later.
1. At the top of the dashboard page, click **Containers**.
1. At the bottom of the Containers page click **Add**.
1. Create a new container named "bundles". Set the **Access** to "Private".
1. Add another container named "public". Set the **Access** to "Public Blob".

## SSL Certification

Codalab allows you to set up SSL Certification for Nginx and RabbitMQ out of the box. Simply place your certs in the /certs dir of the project
root, then point `SSL_CERTIFICATE` and `SSL_CERTIFICATE_KEY` to the correct files respectively.

## Log files

If you use codalab out of the box, you'll notice that we have supplied a persistent logs setup via docker volumes. This maps to _/logs_
in the root of the project directory automatically, however, can be modified in your copy of _.env_

## Service Bus

Codalab uses task queue named Celery, and a message broker named RabbitMQ to handle external requests for the execution of **competition creations**, **submissions**, and other site related tasks.
This allows codalab to operate in a non-blocking way, essentially off loading HUGE tasks onto Celery, and polling it later for the results

### RabbitMQ How To

Codalab sets up an instance of RabbitMQ for you with default settings out of the box. If this does not work for you, you may 
change the `RABBITMQ_DEFAULT_USER` `RABBITMQ_DEFAULT_PASS` `RABBITMQ_PORT` `RABBITMQ_MANAGEMENT_PORT` envs in your local _.env_ file to better suit your setup.

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

Flower is a Celery Monitoring tool that allows you view things such as: memory usage, tasks ran, and the state of any task ran through RabbitMQ.
This can be extremely helpful in troubleshooting any load balancing issues you may have by running tons of tasks.

To set this up, simply set the `FLOWER_BASIC_AUTH` and `FLOWER_PORT` in your local _.env_ file to match your desired setup.

## Nginx How To

Setting up nginx is fairly straightforward