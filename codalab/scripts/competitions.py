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
brats2012,_ = Competition.objects.get_or_create(title=brats12_name, creator=guest1, modified_by=guest1,defaults=dict(description=brats12_description))
details_category = ContentCategory.objects.get(name="Learn the Details")
participate_category = ContentCategory.objects.get(name="Participate")
pc,_ = PageContainer.objects.get_or_create(object_id=brats2012.id, content_type=ContentType.objects.get_for_model(Competition))
brats2012.pagecontent = pc
brats2012.save()

Page.objects.get_or_create(category=details_category, container=pc,  codename="overview",
			   defaults=dict(label="Overview", rank=0,
					 html=open(os.path.join(os.path.dirname(__file__), "brats2012_overview.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="evaluation", 
			   defaults=dict(label="Evaluation", rank=1,
					 html=open(os.path.join(os.path.dirname(__file__), "brats2012_evaluation.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="terms_and_conditions",
                    defaults=dict(rank=2, label="Terms and Conditions", html=open(os.path.join(os.path.dirname(__file__), "brats2012_terms_and_conditions.html")).read()))

Page.objects.get_or_create(category=details_category, container=pc,  codename="faq",
			   defaults=dict(label="FAQ", rank=3, html=open(os.path.join(os.path.dirname(__file__), "brats2012_faq.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="key_dates",
			   defaults=dict(label="Key Dates", rank=4, html=open(os.path.join(os.path.dirname(__file__), "brats2012_key_dates.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="organizers",
			   defaults=dict(label="Organizers", rank=5,html=open(os.path.join(os.path.dirname(__file__), "brats2012_organizers.html")).read()))

Page.objects.get_or_create(category=participate_category, container=pc,  codename="get_data",
                    defaults=dict(label="Get Data", rank=0, html=open(os.path.join(os.path.dirname(__file__), "brats2012_data.html")).read()))
Page.objects.get_or_create(category=participate_category, container=pc,  codename="submit_results", html="", defaults=dict(label="Submit Results", rank=1))

# Logo
brats2012.image = File( open(os.path.join(root_dir, "fixtures", "images", "brats.jpg"), 'rb'))

# Save the updates
brats2012.save()

## Score Definitions

for s in ( {'Dice': {'subs': (('dice_complete','Complete'),('dice_core','Core'),('dice_enhancing','Enhancing'))  } },
	   {'Sensitivity': {'subs': (('sensitivity_complete','Complete'),('sensitivity_core','Core'),('sensitivity_enhancing','Enhancing'))  }},
	   {'Specificity': {'subs': (('specific_complete','Complete'),('specific_core','Core'),('specific_enhancing','Enhancing')) }},
	   {'Hausdorff': {'subs': (('hausdorff_complete','Complete'),('hausdorff_core','Core'),('hausdorf_enhancing','Enhancing'))}},
	   {'Kappa': {'def':  ('kappa','Kappa')}}
	   ):
	for label,e in s.items():
		g,cr = SubmissionScoreGroup.objects.get_or_create(label=label)
		for t,defs in e.items():
			if t == 'subs':
				for sub in defs:
					sd,cr = SubmissionScoreDef.objects.get_or_create(competition=brats2012,key=sub[0],
												defaults=dict(label=sub[1]))
					g2,cr = SubmissionScoreGroup.objects.get_or_create(parent=g,label=sub[1],
												  defaults=dict(scoredef=sd))
					
			elif t == 'def':
				sd,cr = SubmissionScoreDef.objects.get_or_create(competition=brats2012,
											key=defs[0],
											defaults = dict(label=defs[1]))
				g.scoredef = sd
				g.save()
					
	    

# Phases for the competition
day_delta = datetime.timedelta(days=30)
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 7, 6), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 10, 1), datetime.time()), timezone.get_current_timezone())
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 7, 15), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 8, 22), datetime.time()), timezone.get_current_timezone())
p, created = CompetitionPhase.objects.get_or_create(competition=brats2012, phasenumber=1, label="Training Phase",
													start_date=p1date, max_submissions=100)
p, created = CompetitionPhase.objects.get_or_create(competition=brats2012, phasenumber=2, label="Competition Phase",
													start_date=p2date, max_submissions=1)

# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()

# Participants for the competition
participants = [ (statuses[i-2], User.objects.get(username="guest%d" % i)) for i in range(2,len(statuses)+2)]

# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()

# Add participants to the competition with random statuses
for status, participant in participants:
	print "Adding %s to competition %s with status %s" % (participant, brats2012, status)
	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=brats2012, 
																				  defaults={'status':status})
#
#  End BRaTS 2012 ----
#

# Spine Localization
spine_name = "Spine Localization Example"
spine_description = """
	Test for server side execution of evaluation program.
"""
spine,created = Competition.objects.get_or_create(title=spine_name, creator=guest1, modified_by=guest1, 
												  description=spine_description, has_registration=True)

details_category = ContentCategory.objects.get(name="Learn the Details")
participate_category = ContentCategory.objects.get(name="Participate")
pc,_ = PageContainer.objects.get_or_create(object_id=spine.id, content_type=ContentType.objects.get_for_model(Competition))
spine.pagecontent = pc
spine.save()

# Page.objects.get_or_create(category=details_category, container=pc,  codename="overview",
# 			   		defaults=dict(label="Overview", rank=0,
# 					 html=open(os.path.join(os.path.dirname(__file__), "example_overview.html")).read()))
# Page.objects.get_or_create(category=details_category, container=pc,  codename="evaluation", 
# 			   		defaults=dict(label="Evaluation", rank=1,
# 					 html=open(os.path.join(os.path.dirname(__file__), "example_evaluation.html")).read()))
# Page.objects.get_or_create(category=details_category, container=pc,  codename="terms_and_conditions",
#                     defaults=dict(rank=2, label="Terms and Conditions", html=open(os.path.join(os.path.dirname(__file__), "example_terms_and_conditions.html")).read()))
# Page.objects.get_or_create(category=participate_category, container=pc,  codename="get_data",
#                     defaults=dict(label="Get Data", rank=0, html=open(os.path.join(os.path.dirname(__file__), "example_data.html")).read()))
# Page.objects.get_or_create(category=participate_category, container=pc,  codename="submit_results", html="", defaults=dict(label="Submit Results", rank=1))

# Logo
spine.image = File(open(os.path.join(root_dir, "fixtures", "images", "spine.jpg"), 'rb'))

# Save updates
spine.save()

# Phases for the competition
day_delta = datetime.timedelta(days=30)
for phase in [1, 2]:
	phase_start = start_date + (day_delta * phase)
	p, created = CompetitionPhase.objects.get_or_create(competition=spine, phasenumber=phase, label="Phase %d" % phase,
														start_date=phase_start, max_submissions=4)

# Participants for the competition
participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]
# print participants

# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()
# print statuses

# Add participants to the competition with random statuses
for participant in participants:
	status = random.choice(statuses)
	# print "Adding %s to competition %s with status %s" % (participant, spine, status)
	resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=spine, 
																				  defaults={'status':status})
#
#  End Spine Localization ----
#
