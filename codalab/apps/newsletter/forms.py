from django import forms

from .models import NewsletterSubscription


class NewsletterSubscriptionSignUpForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']

        def clean_email(self):
            email = self.cleaned_data.get()

            return email


class NewsletterSubscriptionUnsubscribeForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']

    # Because `unique=True` in the model, we must allow non-unique emails to be valid in our form for unsubscribing
    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError as e:
            del e.error_dict['email']
            self._update_errors(e)
