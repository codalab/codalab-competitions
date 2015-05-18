from django.db import models
from sorl.thumbnail import ImageField
from apps.authenz.models import ClUser
import datetime

# Team details
class Team(models.Model):

    team_id = models.AutoField(primary_key=True)
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

    is_admin = models.BooleanField(default=False)
    date_joined = models.DateField(blank=True)
    user_accepted = models.BooleanField(default=False)
    team_accepted = models.BooleanField(default=False)
    membership_request_message = models.TextField(blank=True)

    # Alternative to composed keys. Check integrity.
    class Meta:
        unique_together = (('team','user'),)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return "Membership: team(" + self.team.name + ") <-> user(" + self.user.username + ")"

    def save(self, *args, **kwargs):
        ''' On save, if membership is accepted by both parts, set the date '''
        if not self.date_joined:
            if self.team_accepted and self.user_accepted:
                self.date_joined = datetime.datetime.today()
        return super(Membership, self).save(*args, **kwargs)
