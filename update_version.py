#!/usr/bin/env python

import subprocess, os

VERSION_FILE="codalab/codalab/settings/version.py"
version = subprocess.check_output(["git", "log", "-n 1", "--pretty=format:\"%H (%aD)\""])
cl_version = "CODALAB_VERSION=\"%s\"" % version

with open(VERSION_FILE, "wb") as file:
	file.write(cl_version)


print "Updated version to: %s" % version