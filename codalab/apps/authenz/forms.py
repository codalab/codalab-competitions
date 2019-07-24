from django import forms
from codalab import settings


class CodalabSignupForm(forms.Form):
    """
    Base sign up form
    """
    team_name = forms.CharField(max_length=64, required=False)
    contact_email = forms.EmailField(required=False)
    if settings.MAILCHIMP_API_KEY:
        newsletter_opt_in = forms.BooleanField(initial=False, required=False)
    method_name = forms.CharField(max_length=20, required=False)
    method_description = forms.CharField(required=False)
    project_url = forms.URLField(required=False)
    publication_url = forms.URLField(required=False)
    organization_or_affiliation = forms.CharField(max_length=255, required=False)
    bibtex = forms.CharField(required=False)

    class Meta():
        widgets = {
            'team_members': forms.Textarea(attrs={"class": "form-control"}),
            'method_description': forms.Textarea(attrs={"class": "form-control"}),
            'bibtex': forms.Textarea(attrs={"class": "form-control"})
        }

    def save(self, new_user):
        new_user.__dict__.update({
            'organization_or_affiliation': self.cleaned_data['organization_or_affiliation'],
            'team_name': self.cleaned_data['team_name'],
            'method_name': self.cleaned_data['method_name'],
            'method_description': self.cleaned_data['method_description'],
            'contact_email': self.cleaned_data['contact_email'],
            'project_url': self.cleaned_data['project_url'],
            'publication_url': self.cleaned_data['publication_url'],
            'bibtex': self.cleaned_data['bibtex'],
        })

        if settings.MAILCHIMP_API_KEY:
            new_user.__dict__.update({
                'newsletter_opt_in': self.cleaned_data['newsletter_opt_in'],
            })
        new_user.save()
