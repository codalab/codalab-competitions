from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from apps.web.models import Competition,CompetitionPhase,CompetitionDataset,CompetitionParticipant,ExternalFile,ExternalFileType,ParticipantStatus

from optparse import make_option

import random
import datetime

import pytz

class Command(BaseCommand):
    help = "Creates competition."

    option_list = BaseCommand.option_list + (
        make_option('--title',
                    dest='title',
                    help="Name ofthe competition"),
        make_option('--description',
                    dest='description',
                   help="Description of the competition"),
        make_option('--creator',
                    dest='creator',
                    help="Email address of creator"),
        
                )
    def handle(self,*args,**options):
        creator_email = options['creator']
        title = options['title']
        description = options['description']
        if not creator_email or not title or not description:
            print "Need a title, description and email of creator"
            exit(1)
        creator = User.objects.get(email=creator_email)
        competition = Competition.objects.create(title=title,
                                                 creator=creator,
                                                 modified_by=creator,
                                                 description=description)
        
 
