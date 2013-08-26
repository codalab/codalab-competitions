#!/usr/bin/env bash
#
#
# This shell script can be used to run the non-production app in a psuedo-production way so that
# we can test it and work on it in an azure instance.
#
# 

# Activate the virtual environment
if [ -x 'venv' ]; then
    source ./venv/bin/activate
else
	echo "Virtual Environment has not been initialized. Exiting."
	echo "You can initialize this by running dev_setup.sh."
	exit 1
fi

STARTUP="codalab/config/generated/startup_env.sh"
# Check for settings
if [ -e $STARTUP ]; then
	echo "Sourcing django configuratoin setup."
	source $STARTUP
else
	echo "Startup configuration not present. Did you run 'python manage.py config_gen' yet?"
	exit 1
fi

# Go to the lower level directory
cd codalab

# Run the django app using nohup (man nohup), so it continues to run after you log out.
nohup python ./manage.py runserver 0.0.0.0:8000 2>&1 >& codalab.output &

# Run the celery process
nohup python ./manage.py celery worker -P solo 2>&1 >& celery.output &

# Exit cleanly
exit 0
