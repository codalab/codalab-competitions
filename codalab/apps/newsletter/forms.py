from django import forms

from .models import NewsletterUser, Newsletter


class NewsletterUserSignUpForm(forms.ModelForm):
    class Meta:
        model = NewsletterUser
        fields = ['email']

        def clean_email(self):
            email = self.cleaned_data.get()

            return email


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = [
            'subject',
            'body',
            'status',
        ]
