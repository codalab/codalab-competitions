# CodaLab [![Circle CI](https://circleci.com/gh/codalab/codalab-competitions.svg?style=shield)](https://circleci.com/gh/codalab/codalab-competitions)

## What is CodaLab?

CodaLab is an open-source web-based platform that enables researchers, developers, and data scientists to collaborate, with the goal of advancing research fields where machine learning and advanced computation is used.  CodaLab helps to solve many common problems in the arena of data-oriented research through its online community where people can share worksheets and participate in competitions.

To see Codalab Competition's in action, visit [www.competitions.codalab.org](https://competitions.codalab.org/).

## Competition's Documentation

- [CodaLab Wiki](https://github.com/codalab/codalab/wiki)

## Community

The CodaLab community forum is hosted on Google Groups.
- [CodaLabDev Google Groups Forum](https://groups.google.com/forum/#!forum/codalabdev)


## Compute worker

To start the compute worker under project directory:

`docker-compose up worker`

If for some reason you need to rebuild the image run:

`docker-compuse up --build worker`

## Staging Server

To ssh into the staging server:

`ssh -i /path/to/pem ubuntu@ec2-34-209-94-162.us-west-2.compute.amazonaws.com`

Pull the most recent copy of project

`cd codalab-competitions`

Run `docker-compose up -d`

If docker is not working, or you need to restart all of the containers

`$(docker ps -a) restart`

## Tests

To run tests:


`python manage.py test`


```python manage.py test```


## Latest changes:
###### November 21, 2016:
New set of credentials to authenticate `BUS SERVICES`. Add the following to `local.py` script.
Leave them empty if previous credentials are provided.
- `SBS_SHARED_ACCESS_KEY_NAME = '<shared access key name>'`
- `SBS_SHARED_ACCESS_KEY_VALUE = '<shared access key value>'`

Add the following to worker config file under `azure-service-bus`
- `shared-access-key-name: "<shared access key name>"`
- `shared-access-key-value: "the key"`

Those values should be available in the Azure dashboard.

