# CodaLab: a platform for

This is CodaLab. It goes to eleven. Just not yet.

## get it working locally

This is all Python. It works on Windows, Linux, Mac and BSD most of the time.
You need two things to start. Well, three things if you count the computer. You
need to have Python 2.7.x installed and a version of pip >= 1.3. 

#### Linux

For current Debian-based Linux distributions , BSD and Mac Python 2.7 is
usually installed. However... Redhat-based Linux distributions, such as RHEL
and CentOS, sometimes behind the curve and do not have python 2.7. As of this
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

If this seems like a lot of steps, it is. There are a couple of ways to do it,
but it is assumed that if you read this far you are a developer of some sort,
have some experience navigating a shell of some sort and/or have an awareness
of the idiosyncratic nature of the platform(s) you employ in you personal and
professional endeavors.

### Virtual Environments

From here you need to have the source checked-out/cloned. If you don't have a
local copy and you are reading this then you have come to the right place. Only
a few clicks will get you where you need to be. 

Assuming that you have a copy, you will need to install the other requirements.
It is best to work in a virtualenv. It is even better to install
virtualenvwrapper:

    pip install virtualenv

For the Linux crowd (and I am also looking at you Mac folks), you will install (probably with sudo):

    pip install virtualenvwrapper

See [here](http://virtualenvwrapper.readthedocs.org/en/latest/).

The Windows contigent can install:

    pip install virtualenvwrapper-powershell

See [here](http://docs.python-guide.org/en/latest/dev/virtualenvs.html) and
[here](http://virtualenvwrapper.readthedocs.org/en/latest/install.html).

### Actual Development

With all the tooling in place, you can create a virtual environment into which
packages can be installed and be kept separate from what is installed on the
system, globally.

    virtualenv MyEnv  # Creates a directory called MyEnv (do this once)

Each time you want to activate the environment, type:

    source MyEnv/bin/activate

The shell prompt should indicate that you're in the environment.

Then, assuming the code is checked out:

    pip install -r codalab/requirements/common.txt

Then to start the CodaLab server:
 
    cd codalab
    python manage.py syncdb  # Need settings.DATABASES (TODO)
    python manage.py runserver
