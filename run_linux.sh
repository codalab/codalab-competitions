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
	exit 1
fi

# Change to the CodaLab directory
cd codalab

# Run the django app using nohup (man nohup), so it continues to run after you log out.
nohup python manage.py runserver 0.0.0.0:8000 2>&1 >& codalab.output &

# Exit cleanly
exit 0