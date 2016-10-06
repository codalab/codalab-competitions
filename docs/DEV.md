Codalab Development
===================

`codalab-competitions` is composed of:

- the frontend, built with Javascript & Python (Django),
- the backend which deals with processing bundles and submissions, built with Python and Microsoft Azure services.


### 0. Getting the source code:

We use git and github for saving, sharing and reviewing code.
You'll need a version of `git` installed on your system.

You can clone the main repository directly:

```
git clone https://github.com/codalab/codalab-competitions.git
```

If you intend to make changes to the codebase, push them back to github and propose these changes
to the main repository (pull requests) you should create your own fork:

1. [Fork](https://help.github.com/articles/fork-a-repo) the CodaLab repo from GitHub.
2. Clone your fork `git clone https://github.com/<username>/codalab-competitions.git`


The rest of the documentation assumes that you've cloned the repository and are
located in the root folder of the project `codalab-competitions/`.


## Competitions Frontend:

It requires python2.7 with Django and a relational database supported by Django (SQLite, MySQL, etc).


### 1. Create a new python virtualenv and install the required packages,

With `python2.7`, `pip` (python package manager) and `virtualenv` on your system, install
the content of `codalab/requirements/common.txt`.

With [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) (recommended):

```
mkvirtualenv -p python2 codalab
workon codalab
pip install -r ./codalab/requirements/common.txt
```

The following assumes you've setup the virtual environment and activated it (`workon codalab`).


### 2. Run an SQL Database

You may use whichever SQL database is supported by our version of django.

We provide a docker compose file that will setup and start a MySQL database for you. 
With [`docker`](https://www.docker.com/) installed, run

```
docker-compose up
```

This will start the database. Note that later this command will also be used to start
the whole development environment without having install any package.


### 3. Configure Django

The local configuration file `local.py` tells CodaLab which type of database you are using, 
and stores credentials for the database.

1. Copy the sample to the path Django will load on start-up:
  - `cp codalab/settings/local_sample.py codalab/settings/local.py`.
2. Open the file in an editor and follow the comments to update the database configuration.
  - We'll configure the bundle parts later.


### 4. Initialize the database

To initialize the database, you will need to run a few django commands and the 
codalab initialization script.

```
cd codalab
python manage.py # Show up the django help and available commands.
python manage.py validate # Validates the database models and output potential errors.
python manage.py syncdb --migrate # synchronizes the database models with the current database running.
python scripts/initialize.py # Insert initial data into your database
```

You'll need to run `validate` and `syncdb --migrate` every time the models changes 
(pulling new version, or adding features). 


### 5. Run the tests

Check that everything is working by running the tests:

```
python manage.py test
```

If you're on master, they should all pass and you'll see something similar to:

```
.......
----------------------------------------------------------------------
Ran 212 tests in 72.022s

OK
Destroying test database for alias 'default'...
```


### 6. Populate sample data

TODO, see issue #1600


### 7. Run the server

Once the setup is complete, with the database running and the codalab virtual environment ready,
run:

```
python manage.py runserver
```

The server should be accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

Most features requires the backend running (uploading competitions bundles and submitting).


## Competitions Backend

Codalab relies on Microsoft Azure services to store data, run workers and queue tasks between
the frontend and the workers.

You'll need a Microsoft Azure subscription for this. The following describes what you need
and attempts to describe the process on the current 
version of the [portal](https://portal.azure.com/).

### 1. Create the storage containers

You need a `storage account` with 2 containers:

- a `blob` called `bundles` in `private` mode
- a `blob` called `public` in `public` mode

The storage account need a relaxed CORS (Cross-Origin Resource Sharing) policy for your local
browser to be able to modify the remote Azure env.

- allowed origin = `*`, methods = `PUT`, headers = `*`, max age = `1800` seconds

Note: these are relaxed policies for a dev env.

*As of October 2016:*

1. On the dashboard, go to `storage accounts (classic)` (left panel)
2. give it a recognizable name, you may leave the default configurations.
  - Be careful with the "resource group", it'll be easier to keep all the resources (storage & service bus)
    under the same group for simpler management.
3. Once created, go to the `Access Keys`, note:
  - the `storage account name` that you gave
  - the `primary access key`, which is an ~ 80 characters long string of random letters and numbers,
4. Go to `blob service > containers`
    - create the containers described previously
5. Go to `blob service > CORS`
    - Add the CORS rule describe previously

### 2. Create the service bus

You need a `service bus account` with 2 queues:
  - `compute` and `responses`
  
The current implementation of Codalab relies on ACS authentication, 
which is deprecated by Microsoft, it can be created through the command line:

*As of October 2016:*

1. With the node package manage installed (`npm`) installed, get the [`azure-cli`](https://www.npmjs.com/package/azure-cli)
  - `npm install -g azure-cli` (the installation is system-wide)
2. `azure login`, follow the instruction to login
3. `azure config mode asm` to switch to the azure service management mode
4. `azure sb namespace create codalabdevsb 'West Europe'`
  - you can customize the name and the region (`West US`, etc). 
  - If it fails you probably used unauthorized characters
    in the name.
5. In the [old portal](https://manage.windowsazure.com), `service bus > the one you just created`
6. Click on the key `Connection Information` at the bottom,
  - Note the `default issuers` and the `default key` from the `ACS` section.
7. Go in the queue section and create the queues described previously with default parameters.


### 3. Update your configuration

Open your `codalab/settings/local.py`,
update the `storage` and `service bus` sections with the values you noted previously.

Copy the sample worker config to its regular location:
`cp codalabtools/compute/sample.config codalabtools/compute/.codalaconfig`

Open the `.codalabconfig` and update it.


### 4. Start the workers

With the codalab virtual environment active,

- `cd codalab/codalab && python worker.py` for the first worker
- `cd codalab/codalabtools/compute/ && python worker.py`

















