from django.utils.timezone import now
from django import forms
from .models import Team, TeamMembership
from tinymce.widgets import TinyMCE
#from awesome_avatar import forms as avatar_forms
import os


class TeamEditForm(forms.ModelForm):
    name = forms.CharField(max_length=64, required=False)
    description = forms.Textarea()
    allow_requests = forms.BooleanField(required=False)
    image = forms.ImageField(required=False)

    #image = avatar_forms.AvatarField()

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
        """
        if competition.participants.filter(user__in=[self.request.user]).exists():
            participant = competition.participants.get(user=self.request.user)
            if participant.status.codename == ParticipantStatus.APPROVED:
                if team.allow_requests:
                    if team.creator!=participant.user and team.is_active and team.is_accepted:
                        current_requests=TeamMembership.objects.filter(
                            team=team,
                            user=participant.user,
                        ).all()
                        if len(current_requests)==0:
                            open_requests=None
                        else:
                            open_requests=None
                            for req in current_requests:
                                if req.is_active:
                                    open_requests=req
                                    break

                        if open_requests is None:
                            TeamMembership.

                    else:
                        error = "You cannot modify this request"
                else:
                    error = "Invalid request: This request is not active"
                context=super(RequestTeamView, self).get_context_data(**kwargs)

                if error is not None:
                    context['error'] = error
        """