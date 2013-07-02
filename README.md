# codalab

This is CodaLab. It goes to eleven. Just not yet.

## get it working locally

This is all Python. It works on Windows, Linux, Mac and BSD most of the time. You need two things to start. Well, three things if you count the computer. You need to have Python 2.7.x installed and a version of pip >= 1.3. 

#### *nixes

For current Debian-based Linux distributions , BSD and Mac Python 2.7 is usually installed. However... Redhat-based Linux distributions, such as RHEL and CentOS, sometimes behind the curve and do not have python 2.7. As of this writing, CentOS 6.4 is at Python 2.6, which is well on its way to EOL. Python 2.6 may work, but code will be written with 2.7 and 3.3+ in mind. 

#### *dows

For Windows you can install Python from here (be sure to select the correct one for you architecture):

  http://www.python.org/download/releases/2.7.5/
  
To Install Pip you should install distribute. Download the following URL:

  http://python-distribute.org/distribute_setup.py

Run it from a shell from the directory into where it was downloaded:
  
```
python distribute_setup.py
```

Or, execute it from Explorer if file associations were setup.

You can then execute from a command-line:

```
easy_install pip
```

Note that 'easy_install.exe' will be located in the Scripts directory of your Python installation. You may find it easier to add the Scripts folder to your environment's PATH variable.

If this seems like a lot of steps, it is. There are a couple of ways to do it, but it is assumed that if you read this far you are a developer of some sort, have some experience navigating a shell of some sort and/or have an awareness of the idiosyncratic nature of the platform(s) you employ in you personal and professional endeavors.

### Virtual Environments

From here you need to have the source checked-out/cloned. If you don't have a local copy and you are reading this then you have come to the right place. Only a few clicks will get you where you need to be. 

Assuming that you have a copy, you will need to install the other requirements. It is best to work in a virtualenv. It is even better to install virtualenvwrapper:

```
pip install virtualenv
```

For the *nix crowd (and I am also looking at you Mac folks), you will install (probably with sudo):

```
pip install virtualenvwrapper
```

See http://virtualenvwrapper.readthedocs.org/en/latest/

The *dows contigent can install from the Windows PowerShell command-line shell:

```
pip install virtualenvwrapper-powershell
$env:WORKON_HOME="~/Envs"
mkdir $env:WORKON_HOME
import-module virtualenvwrapper
```

See http://docs.python-guide.org/en/latest/dev/virtualenvs.html
and http://virtualenvwrapper.readthedocs.org/en/latest/install.html

### Actual Development

With all the tooling in place, you can create a virtual environment into which packages can be installed and be kept separate from what is installed on the system, globally. 

```
mkvirtualenv MyEnv
```

It should create it and activate the environment. The shell prompt should indicate it, but if it doesn't you should be able to examine the value of the environment variable $VIRTUAL_ENV which should indicate the directory which is the root of the virtual environment.

Then, assuming the code is checked out:

```
pip install -r codalab/requirements/dev.txt
```

Which will install the dependences for a dev environment. 


Then:

```
cd codalab
python manage.py syncdb
python manage.py runserver
```
 
If syncdb fails it will provide an error. If certain python packages and/or Django apps and modules are not installed it will indicate what it cannot find. This usually means that the requirements have not been installed.
