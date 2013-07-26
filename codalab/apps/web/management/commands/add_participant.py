from django.core.management.base import BaseCommand, CommandError
from apps.web.models import Competition,CompetitionParticipant,ParticipantStatus
from apps.authenz.models import User
from optparse import make_option

class Command(BaseCommand):
    help = "Adds a particpant to a competition. If the user does not exist, it will create one."

    option_list = BaseCommand.option_list + (
        make_option('--email',
                    dest='email',
                    help="Email of the user"),
        make_option('--competition',
                    dest='competition',
                    default=None,
                    help="ID of the competition"),
        make_option('--status',
                    choices=('unknown','pending','approved','denied'),
                    dest='status',
                    default='pending',
                    help="The initial status of the created participant"
                    )
        )
    
    def handle(self, *args, **options):
        competition_id = options['competition']
        competition = None
        if not options['email']:
            print " ... Email Required ... "
            exit(1)

        user,cr = User.objects.get_or_create(email=options['email'], defaults={'username': options['email']})
        if cr:
            user.set_password('testing')
            user.save()
            print "\nNew User Created. Password: testing\n"
        while not competition:
            if competition_id:
                try:    
                    competition = Competition.objects.get(pk=competition_id)
                    competition_id = competition.pk
                    break
                except Competition.DoesNotExist:
                    pass
            else:
                print "Competition not specified or not valid:\n"
            clist = Competition.objects.order_by('pk').all()
            if not clist:
                print " ... There are no competitions ..."
                exit(1)
            for c in clist:
                print "  %d) %s" % (c.pk,c.title)
            try:
                competition_id = int(raw_input("\n Enter number --> "))
            except ValueError:
                print " ... Bad Input ... "
                competition_id = None
                continue
        pstatus = ParticipantStatus.objects.get(codename=options['status'])
        part,cr = CompetitionParticipant.objects.get_or_create(user=user,
                                                               competition=competition,
                                                               defaults={'status':pstatus})
        if not cr:
            print " ... Participant already exists ... "
        
           

        
        
