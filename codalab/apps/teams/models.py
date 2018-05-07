import logging
import os
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.functional import cached_property
from django import template
import apps.web as web
from apps.web.utils import PublicStorage, BundleStorage
from datetime import datetime, timedelta

register = template.Library()
User = settings.AUTH_USER_MODEL
logger = logging.getLogger(__name__)


def get_competition_teams(competition):
    team_list=Team.objects.filter(
        competition=competition,
        status=TeamStatus.objects.get(codename="approved"),
    ).all()
    return team_list


def get_competition_pending_teams(competition):
    team_list=Team.objects.filter(
        competition=competition,
        status=TeamStatus.objects.get(codename="pending"),
    ).select_related("status").all()

    return team_list


def get_team_pending_membership(team):
    requests = TeamMembership.objects.filter(
        team=team,
        is_request=True,
        status=TeamMembershipStatus.objects.get(codename="pending"),
    ).select_related("user").all()
    return requests


def get_competition_deleted_teams(competition):
    team_list=Team.objects.filter(
        competition=competition,
        status=TeamStatus.objects.get(codename="deleted"),
    ).all()

    return team_list


def get_competition_user_teams(competition,user):
    team_list=Team.objects.filter(
        competition=competition,
        status=TeamStatus.objects.get(codename="approved"),
        creator=user.user,
    ).all()
    if len(team_list)==0:
        team_list=None
    else:
        team_list=team_list[0]
    return team_list


def get_competition_user_pending_teams(competition,user):
    team_list=Team.objects.filter(
        competition=competition,
        status=TeamStatus.objects.get(codename="pending"),
        creator=user.user,
    ).all()
    if len(team_list)==0:
        team_list=None
    else:
        team_list=team_list[0]
    return team_list


def get_user_requests(user, competition):
    team_list = get_competition_teams(competition)
    user_requests = TeamMembership.objects.filter(
        user=user.user,
        team__in=team_list,
    ).all()
    return user_requests


def get_allowed_teams(user,competition):
    # TODO: Remove teams where user already have a request
    return get_competition_teams(competition)


def get_user_team(user, competition):
    team = get_competition_user_teams(competition, user)

    if team is not None:
        return team

    user_requests = get_user_requests(user, competition)
    user_team = user_requests.filter(status=TeamMembershipStatus.objects.get(codename="approved")).all()
    if len(user_team) == 0:
        user_team = None

    if user_team is not None:
        for req in user_team:
            if req.is_active:
                team = req

    if team is not None:
        team = team.team

    return team


def get_team_submissions(team, phase=None):
    if phase is None:
        t_s = web.models.CompetitionSubmission.objects.filter(phase=phase, team=team)
    else:
        t_s = web.models.CompetitionSubmission.objects.filter(team=team)

    return t_s


def get_last_team_submissions(team, days=1):
    return web.models.CompetitionSubmission.objects.filter(team=team, submitted_at__gte=datetime.now()-timedelta(days))


def get_team_submissions_inf(team, phase):

    submissions = web.models.CompetitionSubmission.objects.filter(
        team=team,
        phase=phase
    ).select_related('status').order_by('-submitted_at')

    # find which submission is in the leaderboard, if any and only if phase allows seeing results.
    id_of_submission_in_leaderboard = -1
    if phase and not phase.is_blind:
        leaderboard_entry = web.models.PhaseLeaderBoardEntry.objects.filter(
            board__phase=phase,
            result__team=team
        ).select_related('result', 'result__participant')
        if leaderboard_entry:
            id_of_submission_in_leaderboard = leaderboard_entry[0].result.pk
    submission_info_list = []
    for submission in submissions: 
        submission_info = {
            'id': submission.id,
            'number': submission.submission_number,
            'username': submission.participant.user.username,
            'filename': submission.get_filename(),  # left as call for legacy update of readable_filename on subs.
            'submitted_at': submission.submitted_at,
            'status_name': submission.status.name,
            'is_finished': submission.status.codename == 'finished',
            'is_in_leaderboard': submission.id == id_of_submission_in_leaderboard,
            'exception_details': submission.exception_details,
            'description': submission.description,
            'team_name': submission.team_name,
            'method_name': submission.method_name,
            'method_description': submission.method_description,
            'project_url': submission.project_url,
            'publication_url': submission.publication_url,
            'bibtex': submission.bibtex,
            'organization_or_affiliation': submission.organization_or_affiliation,
            'is_public': submission.is_public,
            'score': submission.get_default_score(),
        }
        submission_info_list.append(submission_info)

    return submission_info_list


def get_available_participants(competition):
    return []


class TeamStatus(models.Model):
    UNKNOWN = 'unknown'
    DENIED = 'denied'
    APPROVED = 'approved'
    PENDING = 'pending'
    DELETED = 'deleted'
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Team(models.Model):
    """ This is the base team. """
    class Meta:
        unique_together = (('name', 'competition'),)

    def __unicode__(self):
        return "[%s] %s - %s" % (self.status.codename, self.competition.title, self.name)

    name = models.CharField(max_length=100)
    competition = models.ForeignKey('web.Competition')
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='team_logo', storage=PublicStorage, null=True, blank=True, verbose_name="Logo")
    image_url_base = models.CharField(max_length=255)
    allow_requests = models.BooleanField(default=True, verbose_name="Allow requests")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='team_creator')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='TeamMembership', blank=True, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(TeamStatus, null=True)
    reason = models.CharField(max_length=100,null=True,blank=True)

    def save(self, *args, **kwargs):
        # Make sure the image_url_base is set from the actual storage implementation
        self.image_url_base = self.image.storage.url('')
        self.last_modified=now()

        if self.status is None:
            self.status = TeamStatus.objects.get(codename=TeamStatus.PENDING)

        # Do the real save
        return super(Team,self).save(*args,**kwargs)

    @cached_property
    def image_url(self):
        # Return the transformed image_url
        if self.image:
            return os.path.join(self.image_url_base, self.image.name)
        return None

    @cached_property
    def active_members(self):
        return self.get_members("approved")

    @cached_property
    def active_requests(self):
        return self.get_members("pending")

    def has_applied(self, user):
        for member in self.get_members("pending"):
            if member.user == user:
                return True
        return False

    def is_member(self, user):
        for member in self.get_members("approved"):
            if member.user == user:
                return True
        return False

    @property
    def is_admin(self, user):
        return self.creator==user

    def get_members(self, status):
        requests = TeamMembership.objects.filter(
            team=self,
            is_request=True,
            status=TeamMembershipStatus.objects.get(codename=status),
        ).select_related("user").all()

        members=[]
        for member in requests:
            if member.is_active:
                members.append(member)

        return members


class TeamMembershipStatus(models.Model):
    UNKNOWN = 'unknown'
    REJECTED = 'rejected'
    APPROVED = 'approved'
    PENDING = 'pending'
    CANCELED = 'canceled'
    name = models.CharField(max_length=30)
    codename = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class TeamMembership(models.Model):
    def __unicode__(self):
        return "%s - %s" % (self.team_id, self.user_id)

    @property
    def is_active(self):
        if self.start_date is not None and now() < self.start_date:
            return False
        if self.end_date is not None and now() > self.end_date:
            return False

        return True

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    team = models.ForeignKey(Team)
    is_invitation = models.BooleanField(default=False)
    is_request = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Start Date")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="End Date")
    message = models.TextField(null=True, blank=True)
    status = models.ForeignKey(TeamMembershipStatus, null=True)
    reason = models.CharField(max_length=100,null=True,blank=True)
