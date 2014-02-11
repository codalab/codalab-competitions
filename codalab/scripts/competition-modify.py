#!/usr/bin/env python
# Run this with the python from the CodaLab virtual environment
#

import sys
import os.path
import os

root_dir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

from apps.web.models import *

for c in Competition.objects.all():
    print c.id, c.title
#    if c.id in (1,2):
#        c.delete()
