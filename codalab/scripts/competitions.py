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

from django.core.files import File
from django.contrib.auth import get_user_model
from apps.web.models import Competition, ParticipantStatus, CompetitionParticipant, CompetitionPhase, CompetitionPageSection, CompetitionPageSubSection

User = get_user_model()

# Get a user to be the creator
guest1 = User.objects.get(username="guest1")

# Basic Pages
# Default pages
ltdp = CompetitionPageSection.objects.create(title="Learn the details", slug="details")
ltdp.save()
pp = CompetitionPageSection.objects.create(title="Participate", slug="participate")
pp.save()
rp = CompetitionPageSection.objects.create(title="See the results", slug="results")
rp.save()
# Default sections
ltdpo = CompetitionPageSubSection(title="Overview", slug="overview", content="Use this page to give an overall description of the competition.", section=ltdp)
ltdpo.save()
ltdpe = CompetitionPageSubSection(title="Evaluation", slug="evaluation", content="Use this page to specify how the evaulation of results will be conducted.", section=ltdp)
ltdpe.save()
ltdpt = CompetitionPageSubSection(title="Terms and Conditions", slug="terms", content="Use this page to specify terms and conditions that participant must agree to.", section=ltdp)
ltdpt.save()
ppg = CompetitionPageSubSection(title="Get data", slug="getdata", content="Use this page to give participants access to the data of the competition.", section=pp)
ppg.save()

# BRaTS 2012
brats12_name = "MICCAI Multimodal Brain Tumor Segmentation (BRaTS) Challenge 2012"
brats12_description = """
	The BRaTS challenge is designed to gauge the current state-of-the-art in automated brain tumor segmentation 
	and to compare between different methods. It is organized in conjuction with the MICCAI 2012 conference.
	"""
brats_logo = open(os.path.join(root_dir, "fixtures", "images", "brats.jpg"), 'rb')
brats2012 = Competition.objects.create(title=brats12_name, creator=guest1, modified_by=guest1, description=brats12_description)
brats2012.image = File(brats_logo)
brats2012.page_sections.add(ltdp)
brats2012.page_sections.add(pp)
brats2012.page_sections.add(rp)
brats2012.save()

# Basic Pages
# Default pages
ltdp = CompetitionPageSection.objects.create(title="Learn the details", slug="details")
ltdp.save()
pp = CompetitionPageSection.objects.create(title="Participate", slug="participate")
pp.save()
rp = CompetitionPageSection.objects.create(title="See the results", slug="results")
rp.save()
# Default sections
ltdpo = CompetitionPageSubSection(title="Overview", slug="overview", content="Use this page to give an overall description of the competition.", section=ltdp)
ltdpo.save()
ltdpe = CompetitionPageSubSection(title="Evaluation", slug="evaluation", content="Use this page to specify how the evaulation of results will be conducted.", section=ltdp)
ltdpe.save()
ltdpt = CompetitionPageSubSection(title="Terms and Conditions", slug="terms", content="Use this page to specify terms and conditions that participant must agree to.", section=ltdp)
ltdpt.save()
ppg = CompetitionPageSubSection(title="Get data", slug="getdata", content="Use this page to give participants access to the data of the competition.", section=pp)
ppg.save()

# Phases for the competition
start_date = datetime.date.today()
day_delta = datetime.timedelta(days=30)
for phase in [1, 2]:
	p, created = CompetitionPhase.objects.get_or_create(competition=brats2012, phasenumber=phase, label="Phase %d" % phase,
														start_date=start_date + (day_delta * phase), max_submissions=4)

# Participants for the competition
participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]
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
	print "Adding %s to competition %s with status %s" % (participant, brats2012, status)
	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=brats2012, 
																				  defaults={'status':status})

#
#
# --------------------------
#
#
# ACM SIG Spatial Cup
sigsc_name = "ACM SIGSPATIAL Cup"
sigsc_description = """
	With the goal of encouraging innovation in a fun way, ACM SIGSPATIAL is hosting an algorithm contest about 
	map matching, which is the problem of correctly matching a sequence of location measurements to roads.
"""
sigsc_logo = open(os.path.join(root_dir, "fixtures", "images", "sigspatial.png"), 'rb')
sigsc, created = Competition.objects.get_or_create(title=sigsc_name, creator=guest1, modified_by=guest1, description=sigsc_description)
sigsc.image=File(sigsc_logo)
sigsc.page_sections.add(ltdp)
sigsc.page_sections.add(pp)
sigsc.page_sections.add(rp)
sigsc.save()
# print sigsc

# Default pages
ltdp = CompetitionPageSection.objects.create(title="Learn the details", slug="details")
ltdp.save()
pp   = CompetitionPageSection.objects.create(title="Participate", slug="participate")
pp.save()
rp = CompetitionPageSection.objects.create(title="See the results", slug="results")
rp.save()

# Default sections
ltdpo = CompetitionPageSubSection(title="Overview", slug="overview", content="Use this page to give an overall description of the competition.", section=ltdp)
ltdpo.save()
ltdpe = CompetitionPageSubSection(title="Evaluation", slug="evaluation", content="Use this page to specify how the evaulation of results will be conducted.", section=ltdp)
ltdpe.save()
ltdpt = CompetitionPageSubSection(title="Terms and Conditions", slug="terms", content="Use this page to specify terms and conditions that participant must agree to.", section=ltdp)
ltdpt.save()
ppg = CompetitionPageSubSection(title="Get data", slug="getdata", content="Use this page to give participants access to the data of the competition.", section=pp)
ppg.save()

# Phases for the competition
start_date = datetime.date.today()
day_delta = datetime.timedelta(days=30)
for phase in [1, 2]:
	p, created = CompetitionPhase.objects.get_or_create(competition=sigsc, phasenumber=phase, label="Phase %d" % phase,
														start_date=start_date + (day_delta * phase), max_submissions=4)

# Participants for the competition
participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]
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

#
#
# -------------------------------
#
#
# Spine Localization
spine_name = "Spine Localization Example"
spine_description = """
	Test for server side execution of evaluation program.
"""
spine_logo = open(os.path.join(root_dir, "fixtures", "images", "spine.jpg"), 'rb')
spine,created = Competition.objects.get_or_create(title=spine_name, creator=guest1, modified_by=guest1, description=spine_description)
spine.page_sections.add(ltdp)
spine.page_sections.add(pp)
spine.page_sections.add(rp)
spine.image = File(spine_logo)
spine.save()

# Phases for the competition
start_date = datetime.date.today()
day_delta = datetime.timedelta(days=30)
for phase in [1, 2]:
	p, created = CompetitionPhase.objects.get_or_create(competition=spine, phasenumber=phase, label="Phase %d" % phase,
														start_date=start_date + (day_delta * phase), max_submissions=4)

# Participants for the competition
participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]
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
	print "Adding %s to competition %s with status %s" % (participant, spine, status)
	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=spine, 
																				  defaults={'status':status})
