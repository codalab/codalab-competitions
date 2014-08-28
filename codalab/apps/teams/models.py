from django.db import models
from sorl.thumbnail import ImageField
from apps.authenz.models import ClUser
import datetime

# Team details
class Team(models.Model):

    teamId = models.AutoField(primary_key=True)
    name = models.URLField(blank=False, unique=True)
    avatar = ImageField(upload_to='team_avatars', blank=True, default='')
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(editable=False)

    members = models.ManyToManyField(ClUser, through="Membership")

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.name;

    def save(self, *args, **kwargs):
        ''' On save, update creation timestamp '''
        if not self.teamId:
            self.creation_date = datetime.datetime.today()
        return super(Team, self).save(*args, **kwargs)

# Team members and their properties
class Membership(models.Model):

    team = models.ForeignKey(ClUser)
    user = models.ForeignKey(Team)

    isAdmin = models.BooleanField(default=False)
    dateJoined = models.DateField(blank=True)
    userAccepted = models.BooleanField(default=False)
    teamAccepted = models.BooleanField(default=False)
    membershipRequestMessage = models.TextField(blank=True)

    # Alternative to composed keys. Check integrity.
    class Meta:
        unique_together = (('team','user'),)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return "Membership: team(" + self.team.name + ") <-> user(" + self.user.username + ")"

    def save(self, *args, **kwargs):
        ''' On save, if membership is accepted by both parts, set the date '''
        if not self.dateJoined:
            if self.teamAccepted and self.userAccepted:
                self.dateJoined = datetime.datetime.today()
        return super(Membership, self).save(*args, **kwargs)
