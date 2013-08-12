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

pip install -r codalab/codalab/requirements/jenkins.txt
