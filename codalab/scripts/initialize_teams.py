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

from apps.teams.models import TeamStatus, TeamMembershipStatus
from django.conf import settings

def insert_data():

    team_status = [ ("Denied", "denied", "Team was denied."),
                    ("Approved", "approved", "Team was approved."),
                    ("Pending", "pending", "Team is pending approval."),
                    ("Deleted", "deleted", "Team has been deleted.")]

    for name, codename, description in team_status:
        _, _ = TeamStatus.objects.get_or_create(name=name, codename=codename, description=description)

    team_membership_status = [ ("Rejected", "rejected", "User membership rejected."),
                    ("Approved", "approved", "User membership approved."),
                    ("Pending", "pending", "User membership is pending approval."),
                    ("Canceled", "canceled", "User membership canceled.")]

    for name, codename, description in team_membership_status:
        _, _ = TeamMembershipStatus.objects.get_or_create(name=name, codename=codename, description=description)


if __name__ == "__main__":

    insert_data()
