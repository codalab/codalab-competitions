from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.contrib.auth.models import User
from apps.web.models import Competition,CompetitionPhase,CompetitionDataset,CompetitionParticipant,ExternalFile,ExternalFileType,ParticipantStatus

from optparse import make_option

import random
import datetime

import pytz

class Command(BaseCommand):
    help = "Creates test competition."

    option_list = BaseCommand.option_list + (
        make_option('--name',
                    dest='name',
                    help="Name ofthe competition"),
        make_option('--email',                    
                    dest='email',
                    help="Email address of user. Will create if doesnt exist"),
        make_option('--number',                    
                    dest='number',
                    type = 'int',
                    help="Number of competitions to create"),
        make_option('--participant',                    
                    dest='participant',
                    help="Participant name prefix. participant2@test.com"),
        make_option('--participant_count',                    
                    dest='participant_count',
                    type='int',
                    default=2,
                    help="Number of participants."),
        make_option('--participant_status',
                    choices=(ParticipantStatus.UNKNOWN,ParticipantStatus.PENDING,ParticipantStatus.APPROVED,ParticipantStatus.DENIED),
                    dest='participant_status',
                    default=ParticipantStatus.PENDING,
                    help="The initial status of the created participants"
                    )
                )
    def handle(self,*args,**options):
        for count in range(1,options['number']+1):
            u,cr = User.objects.get_or_create(email=options['email'],
                                              defaults={'username': options['email']}
                                              )
            if cr:
                u.set_password('testing')
                u.save()
                print "Pasword for user is: testing"
            competition_name = "%s %d" % (options['name'],count)
            c = Competition.objects.create(title=competition_name,
                                           description="This is the description for competition %s" % options['name'],
                                           creator = u,
                                           modified_by = u)
            pstatus = ParticipantStatus.objects.get(codename=options['participant_status'])
            for i in range(1,options['participant_count']+1):
                pname = "%s%d" % (options['participant'],options['participant_count'])
                
                pu,cr  = User.objects.get_or_create(username=pname,
                                                email="%s@test.com" % pname)
                if cr:
                    pu.set_password('testing')
                    pu.save()
                    
                part,cr = CompetitionParticipant.objects.get_or_create(competition=c,
                                                                       user=pu,
                                                                       defaults={
                                                                       'status': pstatus})
                if cr:
                    part.status=pstatus
                    part.save()

            delta = datetime.timedelta(days = 0)
            ftype = ExternalFileType.objects.get(codename='test')

            for i in range(1,3):

                start_date = datetime.datetime.now( pytz.utc) + delta

                f = ExternalFile.objects.create(type=ftype,
                                                source_url = "http://test.com/test/%s" % slugify("%s%d" % (unicode(competition_name),i)) ,
                                                source_address_info = "SPECIFIC_INFO",
                                                creator = u)

                d = CompetitionDataset.objects.create(competition=c,
                                                      number=i,
                                                      datafile = f)

                p = CompetitionPhase.objects.create(competition=c,
                                                    phasenumber=i,
                                                    label="Phase %d" % i,
                                                    start_date=start_date,
                                                    max_submissions=4,
                                                    dataset = d)

                delta = datetime.timedelta(days = 10)                               

                                           
