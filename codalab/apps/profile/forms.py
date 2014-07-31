from apps.authenz.models import ClUser
from apps.profile.models import UserProfile
from django import forms

class UserForm(forms.ModelForm):
    class Meta:
        model = ClUser
        fields = ('first_name', 'last_name')

class UserProfileForm(forms.ModelForm):
    picture = forms.ImageField()
    class Meta:
        model = UserProfile
        fields = ('affiliation', 'location', 'picture', 'biography', 'website')
