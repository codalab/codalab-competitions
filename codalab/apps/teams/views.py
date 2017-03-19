from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, TemplateView
from django.core.urlresolvers import reverse

from apps.web.models import Competition, ParticipantStatus, CompetitionSubmission, get_current_phase
from apps.web.views import LoginRequiredMixin

from .models import Team, TeamStatus, TeamMembership, TeamMembershipStatus, get_user_requests, get_competition_teams, get_user_team, get_allowed_teams, get_team_pending_membership, get_competition_user_pending_teams, get_team_submissions_inf
from apps.teams import forms
from django.views.generic import View, TemplateView, DetailView, ListView, FormView, UpdateView, CreateView, DeleteView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet, NamedFormsetsMixin

from django.db.models import Q
from django.http import Http404, QueryDict
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.http import StreamingHttpResponse

User = get_user_model()

class TeamDetailView(LoginRequiredMixin, TemplateView):
    # Serves the table of submissions in the Participate tab of a competition.
    # Requires an authenticated user who is an approved participant of the competition.
    template_name = 'teams/team_info.html'
    form_class = forms.TeamMembershipForm

    def post(self, request, *args, **kwargs):
        data = QueryDict(request.body)
        form_status = data['status']
        form_req_id = data['request_id']
        form_reason = data['reason']

        membership = TeamMembership.objects.get(pk=form_req_id)

        competition = Competition.objects.get(pk=self.kwargs['competition_pk'])
        if competition.participants.filter(user__in=[membership.user]).exists():
            participant = competition.participants.get(user=membership.user)
            if participant.status.codename == ParticipantStatus.APPROVED:
                if get_user_team(participant, competition) is None:
                    membership.status = TeamMembershipStatus.objects.get(codename=form_status)
                    membership.reason = form_reason
                    if membership.status.codename == TeamMembershipStatus.REJECTED:
                        membership.end_date = now()
                    if membership.status.codename == TeamMembershipStatus.CANCELED:
                        membership.end_date = now()
                    membership.save()

                    # Close other requests
                    if membership.status.codename == TeamMembershipStatus.APPROVED:
                        current_requests = TeamMembership.objects.filter(
                            user=participant.user
                        ).all()
                        for req in current_requests:
                            if req.is_active and req.is_request and req != membership:
                                req.status = TeamMembershipStatus.objects.get(codename=TeamMembershipStatus.CANCELED)
                                req.end_date = now()
                                req.save()

        context = self.get_context_data()

        return super(TeamDetailView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        context['team'] = None
        competition = Competition.objects.get(pk=self.kwargs['competition_pk'])
        context['competition'] = competition

        members_columns = [
            {
                'label': '#',
                'name': 'number'
            },
            {
                'label': 'NAME',
                'name': 'name'
            },
            {
                'label': 'EMAIL',
                'name': 'email'
            },
            {
                'label': 'JOINED',
                'name' : 'joined'
            },
            {
                'label': 'STATUS',
                'name': 'status'
            },
            {
                'label': 'ENTRIES',
                'name': 'entries'
            }
        ]

        if competition.participants.filter(user__in=[self.request.user]).exists():
            participant = competition.participants.get(user=self.request.user)
            if participant.status.codename == ParticipantStatus.APPROVED:
                user_team = get_user_team(participant, competition)

                team_list= get_competition_teams(competition)
                user_requests = get_user_requests(participant, competition)
                user_pending_teams = get_competition_user_pending_teams(competition, participant)
                if user_team is not None:
                    context['team'] = user_team
                    context['team_requests'] = get_team_pending_membership(user_team)
                    owner_part=competition.participants.get(user=user_team.creator)
                    member_list=[
                        {
                            'pk': user_team.creator.pk,
                            'name': user_team.creator.username,
                            'email': user_team.creator.email,
                            'joined': user_team.created_at,
                            'status': 'creator',
                            'number':  1,
                            'entries': len(CompetitionSubmission.objects.filter(team=user_team, participant=owner_part)),
                        }
                    ]
                    s_ap = TeamMembershipStatus.objects.get(codename=TeamMembershipStatus.APPROVED)
                    for number, member in enumerate(user_team.members.all()):
                        membership_set = member.teammembership_set.filter(team=user_team)
                        membership = None
                        member_part=competition.participants.get(user=member)
                        for m in membership_set:
                            if m.status == s_ap:
                                membership = m
                                break
                        if membership is not None:
                            user_entry = {
                                'pk': member.pk,
                                'name': member.username,
                                'email': member.email,
                                'joined': membership.start_date,
                                'status': membership.status.codename,
                                'number': number + 2,
                                'entries': len(CompetitionSubmission.objects.filter(team=user_team, participant=member_part)),
                            }
                            if user_entry['status'] == TeamMembershipStatus.APPROVED and membership.is_active:
                                member_list.append(user_entry)
                    context['team_members']=member_list
                    context['members_columns'] = members_columns
                    context['active_phase'] = get_current_phase(competition)
                    context['submission_info_list'] = get_team_submissions_inf(user_team, context['active_phase'])
                context['requests'] = user_requests
                context['teams'] = team_list
                context['allowed_teams'] = get_allowed_teams(participant, competition)
                context['pending_teams'] = user_pending_teams


        return context

class RequestTeamView(TeamDetailView):
    def get_context_data(self, **kwargs):
        error = None
        action = self.kwargs['action']
        request = TeamMembership.objects.get(pk=self.kwargs['request_pk'])
        competition = Competition.objects.get(pk=self.kwargs['competition_pk'])
        if competition.participants.filter(user__in=[self.request.user]).exists():
            participant = competition.participants.get(user=self.request.user)
            if participant.status.codename == ParticipantStatus.APPROVED:
                if request.is_active:
                    if request.user==participant.user:
                        if action == 'accept':
                            if not request.is_invitation:
                                error="Invalid request type: Cannot accept your own request"
                            else:
                                request.is_accepted=True
                                request.status = TeamMembershipStatus.objects.get(
                                                        codename=TeamMembershipStatus.APPROVED)
                                request.save()
                        elif action == 'reject':
                            if not request.is_invitation:
                                error="Invalid request type: Cannot reject your own request"
                            else:
                                request.end_date=now()
                                request.status = TeamMembershipStatus.objects.get(
                                    codename=TeamMembershipStatus.REJECTED)
                                request.save()
                        elif action == 'cancel':
                            if not request.is_request:
                                error="Invalid request type: Cannot cancel an invitation"
                            else:
                                request.end_date=now()
                                request.status = TeamMembershipStatus.objects.get(
                                    codename=TeamMembershipStatus.CANCELED)
                                request.save()
                    elif request.team.creator==participant.user:
                        if action == 'accept':
                            if request.is_invitation:
                                error="Invalid request type: Cannot accept your own invitation"
                            else:
                                request.is_accepted=True
                                request.status = TeamMembershipStatus.objects.get(
                                    codename=TeamMembershipStatus.APPROVED)
                                request.save()
                        elif action == 'reject':
                            if request.is_invitation:
                                error="Invalid request type: Cannot reject your own invitation"
                            else:
                                request.end_date=now()
                                request.status = TeamMembershipStatus.objects.get(
                                    codename=TeamMembershipStatus.REJECTED)
                                request.save()
                        elif action == 'cancel':
                            if request.is_request:
                                error="Invalid request type: Cannot cancel a request"
                            else:
                                request.end_date=now()
                                request.status = TeamMembershipStatus.objects.get(
                                    codename=TeamMembershipStatus.CANCELED)
                                request.save()
                    else:
                        error = "You cannot modify this request"
                else:
                    error = "Invalid request: This request is not active"
                context=super(RequestTeamView, self).get_context_data(**kwargs)
                context['action']=action

                if error is not None:
                    context['error'] = error

        return context

class NewRequestTeamView(LoginRequiredMixin, CreateView):
    model = TeamMembership
    template_name = "teams/request.html"
    form_class = forms.TeamMembershipForm

    def get_success_url(self):
        competition=Competition.objects.get(pk=self.kwargs['competition_pk']);
        return reverse('team_detail', kwargs={'competition_pk': competition.pk})
    def get_context_data(self, **kwargs):
        context = super(NewRequestTeamView, self).get_context_data(**kwargs)
        context['competition'] = Competition.objects.get(pk=self.kwargs['competition_pk'])
        context['team'] = Team.objects.get(pk=self.kwargs['team_pk'])
        return context
    def form_valid(self, form):
        form.instance.user=self.request.user
        form.instance.team=Team.objects.get(pk=self.kwargs['team_pk'])
        form.instance.start_date=now()
        form.instance.is_request=True
        form.instance.status = TeamMembershipStatus.objects.get(codename=TeamMembershipStatus.PENDING)
        form.save()
        return super(NewRequestTeamView, self).form_valid(form)

class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = "teams/edit.html"
    form_class = forms.TeamEditForm

    def get_success_url(self):
        return reverse('team_edit', kwargs={'competition_pk': self.object.competition.pk,'team_pk':self.object.pk})
    def get_context_data(self, **kwargs):
        context = super(TeamCreateView, self).get_context_data(**kwargs)
        context['competition'] = Competition.objects.get(pk=self.kwargs['competition_pk'])
        return context
    def form_valid(self, form):
        form.instance.creator=self.request.user
        form.instance.created_at=now()
        form.instance.competition=Competition.objects.get(pk=self.kwargs['competition_pk'])
        if form.instance.competition.require_team_approval:
            form.instance.status = TeamStatus.objects.get(codename=TeamStatus.PENDING)
        else:
            form.instance.status = TeamStatus.objects.get(codename=TeamStatus.APPROVED)
        #form.instance.image = form.cleaned_data['image']
        #form.image.save("revsys-logo.png", django_file, save=True)

        if form.instance.image:
            a=form.instance.image


        form.save()
        return super(TeamCreateView, self).form_valid(form)

class TeamEditView(LoginRequiredMixin, UpdateView):
    model = Team
    template_name = "teams/edit.html"
    form_class = forms.TeamEditForm
    pk_url_kwarg = 'team_pk'

    def get_success_url(self):
        return ''
    def get_context_data(self, **kwargs):
        context = super(TeamEditView, self).get_context_data(**kwargs)
        context['competition'] = Competition.objects.get(pk=self.kwargs['competition_pk'])
        context['information'] = {
            'Team name': self.object.name,
            'Description' : self.object.description,
            'Allow Requests': self.object.allow_requests,
            'Image': self.object.image
        }

        return context

    def form_valid(self, form):

        if form.instance.image:
            a=form.instance.image

        form.save()
        return super(TeamEditView, self).form_valid(form)


class TeamCancelView(TeamDetailView):

    def get_context_data(self, **kwargs):
        error = None
        team = Team.objects.get(pk=self.kwargs['team_pk'])
        if team.creator == self.request.user:
            if team.status.codename == 'pending':
                status = TeamStatus.objects.get(codename="deleted")
                team.status = status
                team.save()
            else:
                error = "Invalid request: Only pending teams can be cancelled"
        else:
            error = "Invalid request: Only owner can cancel the team"

        context=super(TeamCancelView, self).get_context_data(**kwargs)
        if error is not None:
            context['error'] = error
        context['team'] = team
        return context