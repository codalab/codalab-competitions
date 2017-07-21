# Debugging

These are several useful commands you may find helpful for debugging.
## Docker Commands
### Logging
To view all currently running containers with docker run ```docker ps```.
This will return you a list of containers and info about them.

To view a specific container's logs, use ```docker logs -f <container-name>``` where `<container-name>` is the name of
the container you wish to view. IE: ```docker logs -f django``` to view django logs. The -f flag is for `follow`.

To view all logs outputs from the project currently ( *Good for debugging several containers* ) use
```docker-compsoe logs -f```. This will stream all logs from all active containers.

List of containers, description, and log use.

| Container        | Description    | Use                                                                         |
|------------------|----------------|-----------------------------------------------------------------------------|
| `django`         | Web Service    | Main container. View many debug prints from various processes.              |
| `postgres`       | Database       | Useful to debug database issues                                             |
| `worker_compute` | Compute Worker | Useful to debug object creation, etc.                                       |
| `worker_site`    | Site worker    | Task manager logs                                                           |
| `nginx`          | Nginx service  | HTTP Service logs                                                           |
| `flower`         | Flower Service | View flower logs                                                            |
| `rabbit`         | Rabbit Service | View rabbit logs                                                            |

To stop streaming logs, press `control+c`.

### Other Commands

Other docker commands that you may find useful:

Use ```docker-compose <command>```. You may also use ```docker-compose <command> <container> <args/flags>```

| Command | Description                                                  | Suggested Usage            |
|---------|--------------------------------------------------------------|----------------------------|
| `up`    | Brings everything into an 'up' state. `-d` is for detatched. | ```docker-compose up -d``` |
| `start` | Starts all containers not running                            | ```docker-compose start``` |
| `stop`  | Stops all active containers                                  | ```docker-compose stop```  |

``docker exec -it <container-name> <program-name>``: Run an interactive terminal inside the container,
with the specified program. IE: ```docker exec -it django bash``` for a bash terminal inside the `django` container.

## Local Testing

To perform py tests locally, go inside of the `django` docker container with ``docker exec -it django bash``.
This will put you in an ```interactive ( -it )``` bash shell within the container.

Next run `py.test` to perform all tests, or if you know the name of the test you'd like to run,
```py.test -k <test-name>```.
The testing printout should revert back to the `django` container bash prompt. From here type `exit` to exit the container.

## Python Commands

These commands are all run through the django container by having bash execute `python`. To get into the django container
with a bash prompt use ```docker exec -it django bash```.

To execute the command use ```python manage.py <command>``` with any appropriate flags or arguments.

|    Command               | Description             | `<parms>` & `--flags`              | Usage                             |
| ------------------------ | ----------------------- | ---------------------------------- | --------------------------------- |
| `createsuperuser`        | Creates a new super user| N/A                                | `createsuperuser`                 |
| `migrate`                | Performs a migration    | `<app>`, `<migration_number>`      | ```migrate web 0059```            |
| `schemamigration`        | Creates a migration     | `<app>`, `<object>`, `--auto`      | ```schemamigration web object```  |
| `create_competition_zip` | Creates a comp bundle   | `-p` or `--numphases` num phases, `-l` or `--phaselength` phase length in mins, `-d` or `--delete` don't delete temp files, `-a` or `--automigrate` auto migrate       | ```create_competition_zip -p 2 -l 5 -d -a``` |
| `create_competition`     | Creates a competition   | `--title` title, `--description` description, `--logo` logo file for comp, `--force_user_create` create user if non-existant, `--creator` creator email, `--numphases` number of phases, `--phasedates` Comma-seprated list of the startdates ```(YYYY-MM-DD, YYYY-MM-DD)``` | ```create_competition ..``` |
| `create_solution`        | Creates a submission    | `d` don't delete temp files, `-w` Wrong. Makes a submission that fails.| `create_solution -d -w`|
| `create_codalab_user`    | Creates a user          | `password`                         | `create_codalab_user "bongo"`     |

## Database

Sometimes it is necessary to destroy, and re-create the database. In those cases use the following commands from
a bash terminal inside the database docker container. IE: ```docker exec -it postgres bash```

```drop <db_name>```

Removes the database with `<db_name>`

```create <db_name>```

Creates a database with `<db_name>`
