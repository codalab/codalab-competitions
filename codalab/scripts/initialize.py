#!/usr/bin/env python
# Run this script from the CodaLab virtual environment to insert
# initial data required by the web app into the database.

import sys, os.path, os

root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

from django.contrib.sites.models import Site
from apps.web.models import (CompetitionSubmissionStatus,
                             ContentCategory,
                             ContentVisibility,
                             DefaultContentItem,
                             ParticipantStatus)
from django.conf import settings

def insert_data():
    """
    Inserts initial data required by the web app into the database defined by the Django settings.

    The script's first action is to check the value of the Site's name. If the name is already the
    expected value (as defined by settings.CODALAB_SITE_NAME) then no additional data is inserted.
    Therefore, it is safe to run the script multiple times; the deployment code takes advantage of
    this fact.
    """
    #
    # Site info
    #

    site, _ = Site.objects.get_or_create(pk=settings.SITE_ID)
    if site.name == settings.CODALAB_SITE_NAME:
        print "Initial data has been detected in the database: skipping all inserts."
        return
    site.domain = settings.CODALAB_SITE_DOMAIN
    site.name = settings.CODALAB_SITE_NAME
    site.save()

    #
    # Initialize web content
    #

    cvs = [ ("Visible", "visible", "viewStateOn"),
            ("Visible Always", "visible_always", "viewStateAlwaysOn"),
            ("Hidden", "hidden", "viewStateOff") ]

    content_visibility_items = dict()
    for name, codename, classname in cvs:
        ncv, _ = ContentVisibility.objects.get_or_create(name=name, codename=codename, classname=classname)
        ncv.save()
        content_visibility_items[codename] = ncv


    ccs = [ { 'parent' : None,
              'name' : "Learn the Details",
              'codename' : "learn_the_details",
              'visibility' : content_visibility_items['visible'],
              'is_menu' : True,
              'content_limit' : 1 },
            { 'parent' : None,
              'name' : "Participate",
              'codename' : "participate",
              'visibility' : content_visibility_items['visible'],
              'is_menu' : True,
              'content_limit' : 1 },
            { 'parent' : None,
              'name' : "Results",
              'codename' : "results",
              'visibility' : content_visibility_items['visible'],
              'is_menu' : True,
              'content_limit' : 1 } ]

    content_categories = dict()
    for category in ccs:
        nc, _ = ContentCategory.objects.get_or_create(parent=category['parent'], name=category['name'],
                            codename=category['codename'], visibility=category['visibility'],
                            is_menu=category['is_menu'], content_limit=category['content_limit'])
        nc.save()
        content_categories[category['codename']] = nc

    cis = [ { 'category' : content_categories['learn_the_details'],
              'initial_visibility' : content_visibility_items['visible'],
              'required' : True,
              'rank' : 0,
              'codename' : "overview",
              'label' : "Overview" },
            { 'category' : content_categories['learn_the_details'],
              'initial_visibility' : content_visibility_items['visible'],
              'required' : True,
              'rank' : 1,
              'codename' : "evaluate",
              'label' : "Evaluate" },
            { 'category' : content_categories['learn_the_details'],
              'initial_visibility' : content_visibility_items['visible'],
              'required' : True,
              'rank' : 2,
              'codename' : "terms_and_conditions",
              'label' : "Terms and Conditions" },
            { 'category' : content_categories['participate'],
              'initial_visibility' : content_visibility_items['visible'],
              'required' : True,
              'rank' : 0,
              'codename' : "get_data",
              'label' : "Get Data" },
            { 'category' : content_categories['participate'],
              'initial_visibility' : content_visibility_items['visible'],
              'required' : True,
              'rank' : 1,
              'codename' : 'submit_results',
              'label' : "Submit/View Results" } ]

    for dci in cis:
        dcii, _ = DefaultContentItem.objects.get_or_create(category=dci['category'], label=dci['label'],
                                rank=dci['rank'], required=dci['required'],codename=dci['codename'],
                                initial_visibility=dci['initial_visibility'])
        dcii.save()


    pss = [ ("Denied", "denied", "Paricipation was denied."),
            ("Approved", "approved", "Paricipation was approved."),
            ("Pending", "pending", "Paricipation is pending approval.") ]

    for name, codename, description in pss:
        _, _ = ParticipantStatus.objects.get_or_create(name=name, codename=codename, description=description)


    submission_status_set = [ ("Submitting", "submitting"),
                              ("Submitted", "submitted"),
                              ("Running", "running"),
                              ("Failed", "failed"),
                              ("Cancelled", "cancelled"),
                              ("Finished", "finished") ]

    for name, codename in submission_status_set:
        _, _ = CompetitionSubmissionStatus.objects.get_or_create(name=name, codename=codename)

if __name__ == "__main__":

    insert_data()
