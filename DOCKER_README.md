## Docker Compose User Guide

In order to get started, make a copy of _settings/local_sample.py_ and call it *settings/local.py* as described in the [CodaLab Wiki](https://github.com/codalab/codalab/wiki)

Uncomment the sections on RabbitMQ and in the Databases section as marked

The docker-compose file in the root of the project will work as is, however, if you would like to change certain variables or ports that is fine.

If everything is working correctly, you may now start your project and all its services:

`docker-compose up -d`

This is will start composing your application in a "detached" mode (recommended for better viewing).

If it is the first time running the command, the services will _"build"_ from their respective images which may take a minute.
You may now inspect that all the containers are running with:

`docker ps -a`

Make note of any information, including the NAME of the containers.

When docker is finally done starting the services, you may view the logs of any given service. E.g to see the db with a name of codalabcompetitions_db_1:

`docker logs -f codalabcompetitions_db_1`

Do this for each service for maximum viewage.

### Troubleshooting Common Docker Issues

Somtimes you may have issues with containers not noticing one another initially. While the docker file is optimized to handle this,
you may find yourself in need of a few more handy tools.

If you need to restart a container to rerun its starup script again, simpy run:

`docker restart <name_of_container>`

You may then do `docker logs -f <name_of_container>` to continue viewing the logs again.

If you ever find yourself modifying the applications Dockerfile for any reason, or feel like rebuilding the project simpy run:

`docker-compose build -d`

This will rebuild any images that do not exist or were otherwise modified.

If you need to inspect any of your containers from the inside, simply use:

`docker exec -it <name_of_container> bash`

This will safely attach you to an interactive terminal inside of the given container. You may exit by typing `exit` at the terminal without fear of killing the container.



 