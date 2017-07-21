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

| Container      | Description    | Use                                                                         |
|----------------|----------------|-----------------------------------------------------------------------------|
| Django         | Web Service    | View data between back-end and front-end, and various containers.           |
| Postgres       | Database       | Useful to debug database issues                                             |
| worker_compute | Compute Worker | Useful to debug object creation. ( Submissions, Competition creation, etc ) |
| worker_site    | Site worker    | Task manager log                                                            |
| nginx          | Nginx service  | HTTP Service logging                                                        |
| flower         | Flower Service | View flower logs                                                            |
| rabbit         | Rabbit Service | View rabbit logs                                                            |

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
`py.test -k <test-name>`.
The testing printout should revert back to `django` container bash prompt. From here type `exit` to exit the container.

## Python Commands

*Todo: add custom manage.py commands*

These commands are all run through a docker-container by having bash execute `python`. To get into a container with a
bash prompt use `docker exec -it <container-name> bash`

To execute the command use `python manage.py <command>` with any appropriate flags or arguments.

|    Command        | Description             | `<parms>` & `--flags`              | Usage                             |
| ----------------- | ----------------------- | ---------------------------------- | --------------------------------- |
| `createsuperuser` | Creates a new super user| N/A                                | `manage.py createsuperuser`       |
| `migrate`         | Performs a migration    | `<app>`, `<migration_number>`      | `manage.py migrate web 0059`      |
| `schemamigration` | Creates a migration     | `<app>`, `<object>`, `--auto`      | `manage.py schemamigration ... `  |

## Database

Sometimes it is necessary to destroy, and re-create the database. In those cases use the following commands from
a bash terminal inside the database docker container. IE: `docker exec -it postgres bash`

`dropdb <db_name>`: Removes the database with `<db_name>`.

`createdb <db_name>`: Creates a database with `<db_name>`.
