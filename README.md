# CodaLab

This is CodaLab. It goes to eleven. Just not yet.

## What is it?

Take a look at the [developing specification](docs/SPECIFICATION.md).

## Local Installation

This is all Python.  It works on Windows, Linux, Mac and BSD most of the time.

### Installing Python

In this section, we will walk you through installing Python 2.7.x and a version
of pip >= 1.3 (for installing Python packages).  You can skip this section if
you already meet these requirements.

#### Linux

For current Debian-based Linux distributions, BSD and Mac Python 2.7 is usually
installed. However... Redhat-based Linux distributions, such as RHEL and
CentOS, sometimes behind the curve and do not have Python 2.7. As of this
writing, CentOS 6.4 is at Python 2.6, which is well on its way to EOL. Python
2.6 may work, but code will be written with 2.7 and 3.3+ in mind. 

#### Windows

For Windows you can install Python from here (be sure to select the correct one
for you architecture):

    http://www.python.org/download/releases/2.7.5/
  
To Install Pip you should install distribute. Download the following URL:

    http://python-distribute.org/distribute_setup.py

Run it from a shell from the directory into where it was downloaded:
  
    python distribute_setup.py

Or, execute it from Explorer if file associations were setup.

You can then execute from a command-line:

    easy_install pip

Note that 'easy\_install.exe' will be located in the Scripts directory of your
Python installation. You may find it easier to add the Scripts folder to your
environment's PATH variable.

If this seems like a lot of steps, it is. There are a couple of ways to do it,
but it is assumed that if you read this far you are a developer of some sort,
have some experience navigating a shell of some sort and/or have an awareness
of the idiosyncratic nature of the platform(s) you employ in you personal and
professional endeavors.

### virtualenv

First, we will install virtualenv, which allows us to create a virtual
environment to keep the CodaLab packages separate from the rest of your system:

    pip install virtualenv

Optionally, you can also install virtualenvwrapper if you want:

    pip install virtualenvwrapper

See [documentation here](http://virtualenvwrapper.readthedocs.org/en/latest).

On Windows, you can install from the Windows PowerShell command-line:

    pip install virtualenvwrapper-powershell
    $env:WORKON_HOME="~/Envs"
    mkdir $env:WORKON_HOME
    import-module virtualenvwrapper

See [here](http://docs.python-guide.org/en/latest/dev/virtualenvs.html) and
[here](http://virtualenvwrapper.readthedocs.org/en/latest/install.html).

### Creating a virtual environment

You can run a single command to install everything you need:

    ./bootstrap 

Or you can follow the following steps if you want to walk through the details.
First create the virtual environment:

    virtualenv venv

This should create a directory <code>venv</code>  To activate the environment:

    source ./venv/bin/activate 

The shell prompt should change to have a <code>(venv)</code> prefix.  To
install all the packages required for CodaLab, run:

    pip install -r codalab/requirements/dev.txt

### Running CodaLab

Now that everything is installed, you can start the CodaLab site:

    cd codalab
    python manage.py syncdb
    python manage.py runserver
    
To load initial data from the initial.json file, you can use this command:

    python manage.py loaddata fixtures/initial.json
 
If syncdb fails it will provide an error.  If certain Python packages and/or
Django apps and modules are not installed it will indicate what it cannot find.
This usually means that the requirements have not been installed.

You should be able to go to [http://127.0.0.1:8000](http://127.0.0.1:8000) to
access your local copy of the website.
