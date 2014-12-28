# CodaLab [![Build Status](https://travis-ci.org/codalab/codalab.png?branch=master)](https://travis-ci.org/codalab/codalab)

## What is CodaLab?

CodaLab is an open-source web-based platform that enables researchers, developers, and data scientists to collaborate, with the goal of advancing research fields where machine learning and advanced computation is used.  CodaLab helps to solve many common problems in the arena of data-oriented research through its online community where people can share worksheets and participate in competitions.

To see CodaLab in action, visit [www.codalab.org](http://www.codalab.org).

## Documentation

- [CodaLab Wiki](https://github.com/codalab/codalab/wiki)
- [CodaLab Online Help](http://www.codalab.org/help)

## Community

The CodaLab community forum is hosted on Google Groups.
- [CodaLabDev Google Groups Forum](https://groups.google.com/forum/#!forum/codalabdev)

## Linux Quickstart

Assume the [codalab-cli repository](https://github.com/codalab/codalab-cli) has
been checked out at the same level as this directory and is called
`../codalab-cli`.

Install all the required Python packages:

    ./dev_setup.sh

Install the standard configuration file.  Edit DATABASES if want to use MySQL
instead of sqlite (need to create a MySQL database separately):

    cp codalab/codalab/settings/local_sample.py codalab/codalab/settings/local.py

Update the database schema:

    cd codalab
    ./manage syncdb --migrate
    ./manage config_gen

In development, CodaLab uses Less to generate CSS, which can be painfully slow.
To turn this off, edit `codalab/codalab/settings/base.py` and make the
following change:

    COMPILE_LESS = False

Start the web server:

    cd codalab
    ./runserver 0.0.0.0:8000

Create an account for `codalab` by navigating to `http://localhost:8000`,
clicking `Sign In`, and Sign Up.  Use any email address starting with
`codalab@`.  This account is just used so we can run the following script:

    source venv/bin/activate
    cd codalab
    python scripts/sample_cl_server_config.py 

This script should print out a fragment of a JSON file with the appropriate
keys, which should be added to the codalab-cli config file (usually
`~/.codalab/config.json`).  This allows the bundle service to authenticate
against the website.  The JSON file looks something like this:

    "auth": {
        "address": "http://localhost:8000",
        "app_id": "...",
        "app_key": "...",
        "class": "OAuthHandler"
    },

Then start the bundle server:

    ../codalab-cli/codalab/bin/cl server

That is it!
