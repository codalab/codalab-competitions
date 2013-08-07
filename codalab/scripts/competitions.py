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
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.web.models import *

# Get the user model
User = get_user_model()

# Deal with time
start_date = timezone.now()

# Get a user to be the creator
guest1 = User.objects.get(username="guest1")

#
#  Start BRaTS 2012 ----
#

# BRaTS 2012
brats12_name = "MICCAI Multimodal Brain Tumor Segmentation (BRaTS) Challenge 2012"
brats12_description = """
	The BRaTS challenge is designed to gauge the current state-of-the-art in automated brain tumor segmentation 
	and to compare between different methods. It is organized in conjuction with the MICCAI 2012 conference.
	"""
brats2012 = Competition.objects.create(title=brats12_name, creator=guest1, modified_by=guest1, description=brats12_description)
details_category = ContentCategory.objects.get(name="Learn the Details")
participate_category = ContentCategory.objects.get(name="Participate")
pc = PageContainer.objects.create(object_id=brats2012.id, content_type=ContentType.objects.get_for_model(Competition))
brats2012.pagecontent = pc
brats2012.save()

Page.objects.create(category=details_category, container=pc, label="Overview", rank=0, codename="overview",
                    html=open(os.path.join(os.path.dirname(__file__), "brats2012_overview.html")).read())
Page.objects.create(category=details_category, container=pc, label="Evaluation", rank=1, codename="evaluation",
                    html=open(os.path.join(os.path.dirname(__file__), "brats2012_evaluation.html")).read())
Page.objects.create(category=details_category, container=pc, label="Terms and Conditions", codename="terms_and_conditions",
                    rank=2, html=open(os.path.join(os.path.dirname(__file__), "brats2012_terms_and_conditions.html")).read())

Page.objects.create(category=details_category, container=pc, label="FAQ", rank=3, codename="faq",
                    html=open(os.path.join(os.path.dirname(__file__), "brats2012_faq.html")).read())
Page.objects.create(category=details_category, container=pc, label="Key Dates", rank=4, codename="key_dates",
                    html=open(os.path.join(os.path.dirname(__file__), "brats2012_key_dates.html")).read())
Page.objects.create(category=details_category, container=pc, label="Organizers", rank=5, codename="organizers",
                    html=open(os.path.join(os.path.dirname(__file__), "brats2012_organizers.html")).read())

Page.objects.create(category=participate_category, container=pc, label="Get Data", rank=0, codename="get_data",
                    html=open(os.path.join(os.path.dirname(__file__), "brats2012_data.html")).read())
Page.objects.create(category=participate_category, container=pc, label="Submit Results", rank=1, codename="submit_results", html="")

# Logo
brats2012.image = File( open(os.path.join(root_dir, "fixtures", "images", "brats.jpg"), 'rb'))

# Save the updates
brats2012.save()

# Phases for the competition
day_delta = datetime.timedelta(days=30)
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 7, 6), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 10, 1), datetime.time()), timezone.get_current_timezone())
p, created = CompetitionPhase.objects.get_or_create(competition=brats2012, phasenumber=1, label="Training Phase",
													start_date=p1date, max_submissions=100)
p, created = CompetitionPhase.objects.get_or_create(competition=brats2012, phasenumber=2, label="Competition Phase",
													start_date=p2date, max_submissions=1)

# Participants for the competition
participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]

# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()

# Add participants to the competition with random statuses
for participant in participants:
	status = random.choice(statuses)
	print "Adding %s to competition %s with status %s" % (participant, brats2012, status)
	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=brats2012, 
																				  defaults={'status':status})
#
#  End BRaTS 2012 ----
#

#
#  Start SIG Spatial Cup ----
#

# # ACM SIG Spatial Cup
# sigsc_name = "ACM SIGSPATIAL Cup"
# sigsc_description = """
# 	With the goal of encouraging innovation in a fun way, ACM SIGSPATIAL is hosting an algorithm contest about 
# 	map matching, which is the problem of correctly matching a sequence of location measurements to roads.
# """
# sigsc, created = Competition.objects.get_or_create(title=sigsc_name, creator=guest1, modified_by=guest1, description=sigsc_description)

# # Default pages
# ltdp = CompetitionPageSection.objects.create(title="Learn the details", slug="details")
# ltdp.save()
# pp = CompetitionPageSection.objects.create(title="Participate", slug="participate")
# pp.save()
# rp = CompetitionPageSection.objects.create(titl="See the results", slug="results")
# rp.save()
# # Default sections
# ltdpo = CompetitionPageSubSection(title="Overview", slug="overview", content="Use this page to give an overall description of the competition.", section=ltdp)
# ltdpo.save()
# ltdpe = CompetitionPageSubSection(title="Evaluation", slug="evaluation", content="Use this page to specify how the evaulation of results will be conducted.", section=ltdp)
# ltdpe.save()
# ltdpt = CompetitionPageSubSection(title="Terms and Conditions", slug="terms", content="Use this page to specify terms and conditions that participant must agree to.", section=ltdp)
# ltdpt.save()
# ppg = CompetitionPageSubSection(title="Get data", slug="getdata", content="Use this page to give participants access to the data of the competition.", section=pp)
# ppg.save()
# sigsc.page_sections.add(ltdp)
# sigsc.page_sections.add(pp)
# sigsc.page_sections.add(rp)

# # Logo
# sigsc.image=File(open(os.path.join(root_dir, "fixtures", "images", "sigspatial.png"), 'rb'))

# # Save the updates
# sigsc.save()
# # print sigsc

# # Phases for the competition
# day_delta = datetime.timedelta(days=30)
# for phase in [1, 2]:
# 	phase_start = start_date + (day_delta * phase)
# 	p, created = CompetitionPhase.objects.get_or_create(competition=sigsc, phasenumber=phase, label="Phase %d" % phase,
# 														start_date=phase_start, max_submissions=4)

# # Participants for the competition
# participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]
# # print participants

# # Participant statuses, if they haven't been created before
# statuses = ParticipantStatus.objects.all()
# # print statuses

# # Add participants to the competition with random statuses
# for participant in participants:
# 	status = random.choice(statuses)
# 	# print "Adding %s to competition %s with status %s" % (participant, sigsc, status)
# 	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=sigsc, 
# 																				  defaults={'status':status})

# #
# #  End SIG Spatial Cup / Start Spine Localization ----
# #

# # Spine Localization
# spine_name = "Spine Localization Example"
# spine_description = """
# 	Test for server side execution of evaluation program.
# """
# spine,created = Competition.objects.get_or_create(title=spine_name, creator=guest1, modified_by=guest1, 
# 												  description=spine_description, has_registration=True)

# # Default pages
# ltdp = CompetitionPageSection.objects.create(title="Learn the details", slug="details")
# ltdp.save()
# pp   = CompetitionPageSection.objects.create(title="Participate", slug="participate")
# pp.save()
# rp = CompetitionPageSection.objects.create(title="See the results", slug="results")
# rp.save()
# # Default sections
# ltdpo = CompetitionPageSubSection(title="Overview", slug="overview", content="Use this page to give an overall description of the competition.", section=ltdp)
# ltdpo.save()
# ltdpe = CompetitionPageSubSection(title="Evaluation", slug="evaluation", content="Use this page to specify how the evaulation of results will be conducted.", section=ltdp)
# ltdpe.save()
# ltdpt = CompetitionPageSubSection(title="Terms and Conditions", slug="terms", content="Use this page to specify terms and conditions that participant must agree to.", section=ltdp)
# ltdpt.save()
# ppg = CompetitionPageSubSection(title="Get data", slug="getdata", content="Use this page to give participants access to the data of the competition.", section=pp)
# ppg.save()
# spine.page_sections.add(ltdp)
# spine.page_sections.add(pp)
# spine.page_sections.add(rp)

# # Logo
# spine.image = File(open(os.path.join(root_dir, "fixtures", "images", "spine.jpg"), 'rb'))

# # Save updates
# spine.save()

# # Phases for the competition
# day_delta = datetime.timedelta(days=30)
# for phase in [1, 2]:
# 	phase_start = start_date + (day_delta * phase)
# 	p, created = CompetitionPhase.objects.get_or_create(competition=spine, phasenumber=phase, label="Phase %d" % phase,
# 														start_date=phase_start, max_submissions=4)

# # Participants for the competition
# participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]
# # print participants

# # Participant statuses, if they haven't been created before
# statuses = ParticipantStatus.objects.all()
# # print statuses

# # Add participants to the competition with random statuses
# for participant in participants:
# 	status = random.choice(statuses)
# 	# print "Adding %s to competition %s with status %s" % (participant, spine, status)
# 	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=spine, 
# 																				  defaults={'status':status})

#
#  End Spine Localization ----
#