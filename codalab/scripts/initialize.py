#!/usr/bin/env python
# Run this with the python from the CodaLab virtual environment
# 

import sys, os.path, os, random, datetime
from django.utils import timezone
# This is a really, really long way around saying that if the script is in
#  codalab\scripts\users.py, we need to add, ../../../codalab to the sys.path to find the settings
root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

from django.core.files import File
from apps.web.models import *

#
# Initialize web content
#

cvs = [
  ("Visible", "visible", "viewStateOn"),
  ("Visible Always", "visible_always", "viewStateAlwaysOn"),
  ("Hidden", "hidden", "viewStateOff"),
  ("Unknown", "unknown", "")
]

content_visibility_items = dict()
for name, codename, classname in cvs:
  ncv, created = ContentVisibility.objects.get_or_create(name=name, codename=codename, classname=classname)
  ncv.save()
  content_visibility_items[codename] = ncv

ccs = [
  { 
    'parent' : None,
    'name' : "Learn the Details",
    'codename' : "learn_the_details",
    'visibility' : content_visibility_items['visible'],
    'is_menu' : True,
    'content_limit' : 1
  },
  { 
    'parent' : None,
    'name' : "Participate",
    'codename' : "participate",
    'visibility' : content_visibility_items['visible'],
    'is_menu' : True,
    'content_limit' : 1
  },
  { 
    'parent' : None,
    'name' : "Results",
    'codename' : "results",
    'visibility' : content_visibility_items['visible'],
    'is_menu' : True,
    'content_limit' : 1
  }
]

content_categories = dict()
for category in ccs:
  nc, created = ContentCategory.objects.get_or_create(parent=category['parent'], name=category['name'], 
                       codename=category['codename'], visibility=category['visibility'], 
                       is_menu=category['is_menu'], content_limit=category['content_limit'])
  nc.save()
  content_categories[category['codename']] = nc

cis = [
  {
    'category' : content_categories['learn_the_details'],
    'initial_visibility' : content_visibility_items['visible'],
    'required' : True,
    'rank' : 0,
    'codename' : "overview",
    'label' : "Overview"
  },
  {
    'category' : content_categories['learn_the_details'],
    'initial_visibility' : content_visibility_items['visible'],
    'required' : True,
    'rank' : 1,
    'codename' : "evaluation",
    'label' : "Evaluation"
  },
  {
    'category' : content_categories['learn_the_details'],
    'initial_visibility' : content_visibility_items['visible'],
    'required' : True,
    'rank' : 2,
    'codename' : "terms_and_conditions",
    'label' : "Terms and Conditions"
  },
  {
    'category' : content_categories['participate'],
    'initial_visibility' : content_visibility_items['visible'],
    'required' : True,
    'rank' : 0,
    'codename' : "get_data",
    'label' : "Get Data"
  },
  {
    'category' : content_categories['participate'],
    'initial_visibility' : content_visibility_items['visible'],
    'required' : True,
    'rank' : 1,
    'codename' : 'submit_results',
    'label' : "Submit Results"
  }
]

for dci in cis:
  dcii, created = DefaultContentItem.objects.get_or_create(category=dci['category'], label=dci['label'],
                            rank=dci['rank'], required=dci['required'],codename=dci['codename'],
                            initial_visibility=dci['initial_visibility'])
  dcii.save()

pss = [
  ("Unknown", "unknown", "Status is unknown."),
  ("Denied", "denied", "Paricipation was denied."),
  ("Approved", "approved", "Paricipation was approved."),
  ("Pending", "pending", "Paricipation is pending approval.")
]

for name, codename, description in pss:
  pstatus, created = ParticipantStatus.objects.get_or_create(name=name, codename=codename, description=description)