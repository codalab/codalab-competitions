from django import forms

from .models import NewsletterSubscription


class NewsletterSubscriptionSignUpForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']

        def clean_email(self):
            email = self.cleaned_data.get()

            return email


class NewsletterSubscriptionUnsubscribeForm(forms.Form):
    email = forms.EmailField(max_length=254)
