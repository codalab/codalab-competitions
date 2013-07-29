#!/usr/bin/env python
# Run this with the python from the CodaLab virtual environment
# 

import sys, os.path, os, random, datetime
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

from django.contrib.auth.models import User
from apps.web.models import Competition, ParticipantStatus, CompetitionParticipant, CompetitionPhase

# Get a user to be the creator
guest1 = User.objects.get(username="guest1")

# # BRaTS 2012
# brats12_name = "MICCAI Multimodal Brain Tumor Segmentation (BRaTS) Challenge 2012"
# brats12_description = """
# 	The BRaTS challenge is designed to gauge the current state-of-the-art in automated brain tumor segmentation 
# 	and to compare between different methods. It is organized in conjuction with the MICCAI 2012 conference.
# 	"""
# brats_logo = os.path.join(root_dir, "fixtures", "images", "brats.jpg")
# brats2012 = Competition.objects.create(title=brats12_name, creator=guest1, modified_by=guest1, description=brats12_description)

# # Spine Localization
# spine_name = "Spine Localization Example"
# spine_description = """
# 	Test for server side execution of evaluation program.
# """
# spine_logo = os.path.join(root_dir, "fixtures", "images", "spine.jpg")
# spine = Competition.objects.create(title=spine_name, creator=guest1, modified_by=guest1, description=spine_description)

# ACM SIG Spatial Cup
sigsc_name = "ACM SIGSPATIAL Cup"
sigsc_description = """
	With the goal of encouraging innovation in a fun way, ACM SIGSPATIAL is hosting an algorithm contest about 
	map matching, which is the problem of correctly matching a sequence of location measurements to roads.
"""
sigsc_logo = os.path.join(root_dir, "fixtures", "images", "sigspatial.jpg")
sigsc, created = Competition.objects.get_or_create(title=sigsc_name, creator=guest1, modified_by=guest1, description=sigsc_description)
# print sigsc

# # Data for the competition phases
# # Fake dataset for now
# datafile = ExternalFile.objects.create(type=External)
# data_set = None

# Phases for the competition
start_date = datetime.date.today()
day_delta = datetime.timedelta(days=10)
for phase in [1, 2]:
	p, created = CompetitionPhase.objects.get_or_create(competition=sigsc, phasenumber=phase, label="Phase %d" % phase,
														start_date=start_date + (day_delta * phase), max_submissions=4)

# Participants for the competition
participants = [ User.objects.get(username="guest%d" % i) for i in [2, 4, 5, 7]]
# print participants

# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()
if len(statuses) == 0:
	print "No statuses created yet, creating them now."
	for status in ['unknown', 'pending', 'approved', 'denied']:
		status_object, created = ParticipantStatus.objects.get_or_create(name=status.capitalize(), codename=status, description="")
	statuses = ParticipantStatus.objects.all()
# print statuses

# Add participants to the competition with random statuses
for participant in participants:
	status = random.choice(statuses)
	print "Adding %s to competition %s with status %s" % (participant, sigsc, status)
	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=sigsc, 
																				  defaults={'status':status})