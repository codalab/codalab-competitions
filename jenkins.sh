#!/usr/bin/env bash
#
# Run jenkins tests / tools
#

if [ -x 'venv' ]; then
   . venv/bin/activate
else
	echo "Virtual environment not setup, exiting."
	exit 1
fi

pip install -r codalab/requirements/jenkins.txt

python codalab/manage.py jenkins

#nosetests --with-xcoverage --with-xunit --cover-erase

#pylint -f parseable . | tee pylint.out