from django.db import models
from sorl.thumbnail import ImageField
from apps.authenz.models import ClUser

# Team details
class Team(models.Model):

    teamId = models.AutoField(primary_key=True)
    name = models.URLField(blank=False, unique=True)
    avatar = ImageField(upload_to='team_avatars', blank=True, default='')
    description = models.TextField(blank=True)
    creation_date = models.DateField(blank=True)

    members = models.ManyToManyField(ClUser, through="Membership")

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.name;

# Team members and their properties
class Membership(models.Model):

    team = models.ForeignKey(ClUser)
    user = models.ForeignKey(Team)

    isAdmin = models.BooleanField(default=False)
    dateJoined = models.DateField(blank=True)
    userAccepted = models.BooleanField(default=False)
    teamAccepted = models.BooleanField(default=False)

    # Alternative to composed keys. Check integrity.
    class Meta:
        unique_together = (('team','user'),)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return "Membership: team(" + self.team.name + ") <-> user(" + self.user.username + ")";
