from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.widgets import ClearableFileInput, Input, CheckboxInput
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from tinymce.widgets import TinyMCE
from django.utils import timezone
from apps.web.models import Competition
from apps.authenz.models import ClUser
from apps.teams.models import TeamMembership, Team, TeamStatus, TeamMembershipStatus
from django.utils.safestring import mark_safe
import os
import datetime


class CustomImageField(ClearableFileInput):

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text, 
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': '',
            }
        template = '%(input)s'
        substitutions['input'] = Input.render(self, name, value, attrs)
        clear_template = '<div class="remove-image"><div class="remove-image btn btn-primary">Remove image</div></div><div class="image-removed">Image removed. Please click Submit to save your changes.</div>' + self.template_with_clear

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = ('<div class="logo-image-container"><img class="logo-image" src="%s" alt="%s"/></div>'
                                        % (escape(value.url),
                                           escape(force_unicode(value))))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = clear_template % substitutions

        return mark_safe(template % substitutions)


class TeamEditForm(forms.ModelForm):
    name = forms.CharField(max_length=64, required=False)
    description = forms.Textarea()
    allow_requests = forms.BooleanField(required=False)
    image = forms.ImageField(required=False, widget=CustomImageField)

    class Meta:
        model = Team
        fields = (
            'name',
            'description',
            'allow_requests',
            'image'
        )
        widgets = {
            'description' : TinyMCE(attrs={'class' : 'team-editor-description'},
                                    mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True, "width" : "100%"})
        }

    def clean_name(self):
        if 'name' in self.changed_data:
            if Team.objects.filter(name=self.cleaned_data['name'], competition_id=self.instance.competition_id).count()>0:
                raise forms.ValidationError("This name is already used by another team", code="duplicated_name")

        return self.cleaned_data["name"]

    def clean_image(self):
        if 'image' in self.changed_data:
            if 'image' in self.files:
                file,ext = os.path.splitext(self.files['image'].name)
                self.files['image'].name = '{0}{1}'.format(self.instance.competition_id , ext)

        return self.cleaned_data["image"]


class TeamMembershipForm(forms.ModelForm):
    message = forms.Textarea()

    class Meta:
        model = TeamMembership
        fields = (
            'message',
        )
        widgets = {
            'message' : TinyMCE(attrs={'class' : 'team-editor-description'},
                                mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True, "width" : "100%"})
        }

    def clean(self):
        cleaned_data = super(TeamMembershipForm, self).clean()

        return cleaned_data


class OrganizerTeamForm(forms.ModelForm):

    text_members = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Team
        fields = ('description', 'name')

    def __init__(self, *args, **kwargs):
        self.user_list = []
        self.competition = Competition.objects.get(pk=kwargs.pop('competition_pk'))
        self.creator = ClUser.objects.get(pk=kwargs.pop('creator_pk'))
        super(OrganizerTeamForm, self).__init__(*args, **kwargs)
        # This check is to see if we have an existing object with a PK, or if we're making a new one
        # If we have an existing we grab existing members for the form.
        if hasattr(self, 'instance'):
            if hasattr(self.instance, 'pk'):
                if self.instance and self.instance.pk:
                    team = Team.objects.get(pk=self.instance.pk)
                    current_members = team.members.all()
                    name_text_list = ""
                    name_list = []
                    for member in current_members:
                        name_list.append(member.username)
                        name_text_list = ",".join(name_list)
                    self.initial['text_members'] = name_text_list

    def clean_text_members(self):
        if self.cleaned_data.get('text_members'):
            team_members_text = self.cleaned_data.get('text_members')
            team_members_list = team_members_text.replace(' ','').split(',')
            # team_members_list = team_members_text.replace(' ','').split('\n')
            self.user_list = ClUser.objects.filter(Q(username__in=team_members_list) | Q(email__in=team_members_list))

    def clean_name(self):
        if self.cleaned_data.get('name'):
            if hasattr(self, 'instance'):
                if self.instance.pk:
                    print("WE HAVE A PK AS WELL IN FORM")
                    existing_team_with_name = Team.objects.filter(name=self.cleaned_data.get('name')).exclude(pk=self.instance.pk)
                    if existing_team_with_name:
                        raise ValidationError(('Invalid value for name. A team already exists with that name.'),
                                              code='invalid')
            else:
                existing_team_with_name = Team.objects.filter(name=self.cleaned_data.get('name'))
                if existing_team_with_name:
                    raise ValidationError(('Invalid value for name. A team already exists with that name.'), code='invalid')
        return self.cleaned_data.get('name')

    def save(self, commit=True):
        self.instance.creator = self.creator
        self.instance.competition = self.competition
        self.instance.status = TeamStatus.objects.get(codename=TeamStatus.APPROVED)

        # We need to call save before adding members
        self.instance.save()

        if hasattr(self, 'user_list'):
            # On save, if we have existing objects, clear it. We only add names in the form.
            if len(self.instance.members.all()) > 0:
                # Remove users no longer in the list
                for user in self.instance.members.all():
                    if user not in self.user_list:
                        # Delete members not on the new list
                        print("Deleting membership for user: {}".format(user))
                        TeamMembership.objects.get(user=user, team=self.instance).delete()
            # Then we loop through the names/emails they gave us.
            for user in self.user_list:
                if user not in self.instance.members.all():
                    # There is not already an existing membership for this user.
                    new_team_membership = TeamMembership.objects.create(
                        user=user,
                        team=self.instance,
                        is_invitation=False,
                        is_request=False,
                        start_date=timezone.now(),
                        end_date=timezone.now() + datetime.timedelta(days=9000),
                        message="Organizer Created",
                        status=TeamMembershipStatus.objects.get(codename=TeamMembershipStatus.APPROVED),
                        reason="Organizer Created Team"
                    )
                    print("Created new membership: {0} for user: {1} on team: {2}".format(new_team_membership, user, self.instance))
                else:
                    print("Existing membership found for user on team.")
        return super(OrganizerTeamForm, self).save(commit=commit)


class OrganizerTeamsCSVForm(forms.Form):

    csv_file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        self.competition = Competition.objects.get(pk=kwargs.pop('competition_pk'))
        self.creator = ClUser.objects.get(pk=kwargs.pop('creator_pk'))
        self.teams_dict = {}
        super(OrganizerTeamsCSVForm, self).__init__(*args, **kwargs)

    def clean_csv_file(self):
        teams_dict = {}
        if self.cleaned_data.get('csv_file'):
            temp_csv = self.cleaned_data.get('csv_file')
            csv_team_list = [line.rstrip() for line in temp_csv]
            for index, value in enumerate(csv_team_list):
                temp_line = value.replace(' ', '').split(',')
                # Pop the team name (First value), into the dict key, then the rest of the list is users.
                teams_dict[temp_line.pop(0)] = temp_line
        self.teams_dict = teams_dict

        for team_name in self.teams_dict:
            if Team.objects.filter(name=team_name):
                raise ValidationError("A team with that name already exists!")

    def save(self):
        if hasattr(self, 'teams_dict'):
            for team_name, team_member_list in self.teams_dict.iteritems():
                new_team = Team.objects.create(
                    name=team_name,
                    competition=self.competition,
                    description=team_name,
                    allow_requests=False,
                    creator=self.creator,
                    created_at=timezone.now(),
                    status=TeamStatus.objects.get(codename=TeamStatus.APPROVED),
                    reason="Organizer Created Team"
                )
                print("Created new team: {}".format(new_team))
                user_list = ClUser.objects.filter(Q(username__in=team_member_list) | Q(email__in=team_member_list))
                for user in user_list:
                    new_team_membership = TeamMembership.objects.create(
                        user=user,
                        team=new_team,
                        is_invitation=False,
                        is_request=False,
                        start_date=timezone.now(),
                        end_date=timezone.now() + datetime.timedelta(days=9000),
                        message="Organizer Created",
                        status=TeamMembershipStatus.objects.get(codename=TeamMembershipStatus.APPROVED),
                        reason="Organizer Created Team"
                    )
                    print("Created new membership for user: {0} on team: {1}".format(user, new_team))
