#!/usr/bin/env python
# Run this with the python from the CodaLab virtual environment
# 

import sys, os.path
sys.path.append(os.path.abspath("../../codalab"))

from django.core.management import setup_environ
from codalab import settings

setup_environ(settings)

from django.contrib.auth.models import User

for i in range(1,11):
 	new_user = User.create(email="guest%d@live.com" % i, username="guest%d" % i)
	new_user.set_password("abc123")
	new_user.save()
