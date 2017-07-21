# Debugging:
 These are several useful commands you may find useful for debugging.
 ## Docker Debug Commands
  ### Logging
  To view all currently running containers with docker run `docker ps`.
  This will return you a list of containers and info about them.

  To view a specific container's logs, use `docker logs -f <container-name>` where `<container-name>` is the name of
  the container you wish to view. IE: `docker logs -f django` to view django logs. The -f flag is for `follow`.

  To view all logs outputs from the project currently ( *Good for debugging several containers* ) use
  `docker-compsoe logs -f`. This will stream all logs from all active containers.

  List of specifics and container description:

  `docker logs -f django`: Django container logs. Shows all web/main site logs.

  `docker logs -f postgres`: Postgres container logs. Shows all database logs.

  `docker logs -f worker_compute`: Worker compute logs. Shows debug info for submissions, competition creation,
  competition dumps, etc.

  `docker logs -f worker_site`: Worker site logs. Distributes tasks to worker_compute.

  `docker logs -f flower`: Flower logs

  `docker logs -f rabbit`: Rabbit logs

  `docker logs -f nginx`: Nginx logs.

  To stop streaming logs, press `control+c`.
  ### Other Commands
  Other docker commands that you may find useful:

  `docker-compose up -d`: Starts all in-active containers and their linked counter-parts. `-d` flag specifies
  detached mode.

  `docker-compose stop` and `docker-compose start`: Stops and starts all docker containers respectively. Can target
  individual containers by specifying them.

  `docker-compose restart`: Restarts all docker-containers. Useful for updating code changes. Can also specify a
  specific container.

  `docker exec -it <container-name> <program-name>`: Run an interactive terminal inside the container,
  with the specified program. IE: `docker exec -it django bash` for a bash terminal inside the `django` container.
 ## Local Testing
  To perform py tests locally, go inside of the `django` docker container with `docker exec -it django bash`.
  This will put you in an `interactive ( -it )` bash shell within the container.

  Next run `py.test` to perform all tests, or if you know the name of the test you'd like to run,
  `py.test -k <test-name>`
  Testing printout should revert back to `django` container bash prompt. From here type `exit` to exit the container.
 ## Python Commands
 -*Todo: add custom manage.py commands*
 These commands are all run through a docker-container by having bash execute `python`. To get into a container with a
 bash prompt use `docker exec -it <container-name> bash`

 `python manage.py createsuperuser`: Interactive python terminal to create a superuser on the codalab instance.

 `python manage.py migrate`: Do not use this unless it is part of a testing procedure. Migrate is for updating the
 models in our database. Usually called like such: `python manage.py migrate <app> <migration_number>`

 `python manage.py schemamigration`: Like above, do not use this unless required. Creates a migration to be used with
 the migrate command. Usually called like such: `python manage.py schemamigration <app> <object> <flags>`
 ## Database

 Sometimes it is necessary to destroy, and re-create the database. In those cases use the following commands from
 a bash terminal inside the database docker container. IE: `docker exec -it postgres bash`

 `dropdb <db_name>`: Removes the database with <db_name>.

 `createdb <db_name>`: Creates a database with <db_name>
