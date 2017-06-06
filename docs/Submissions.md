# Competition Submissions

<h4>How to create new submissions to competitions</h4>

<h2>Step 1</h2>

<h4>This step is really important!</h4>

Remove any queues you have in the competition you are trying to make a new submission for. You can do this by clicking Edit on a competition page, scrolling down to the worker queues field and resetting this field to its default state.  Finally, click save.

## Step 2

#### Ensure the proper permissions are set

`cd codalab-competitions`

`mkdir var`

`sudo chown youruser:youruser -R var`

`mkdir /tmp/codalab`

`sudo hown youruser:youruser -R /tmp/codalab`

`sudo chmod 777 /tmp/codalab`

## Step 3

#### Create and start worker_compute

`docker-compose create worker_compute`

`docker-compose start worker_compute`

## Troubleshooting

`IOError: [Errno 13] Permission denied: ‘/var/log/compute_worker.log’`

If you get an error similar to this, try running the code below.

`docker-compose rm worker_compute`


`docker-compose build worker_compute`

#### Ensure that you have SSL set up. Please see [the SSL section of this guide](/en/latest/1.%20Setup%20Guide%20-%20Docker/) for details.
