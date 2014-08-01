from apps.authenz.models import ClUser
from apps.profile.models import UserProfile
from django import forms
from tinymce.widgets import TinyMCE

class UserForm(forms.ModelForm):
    class Meta:
        model = ClUser
        fields = ('first_name', 'last_name')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('affiliation', 'location', 'picture', 'biography', 'website')
        widgets = { 'biography' : TinyMCE(attrs={'rows' : 20, 'class' : 'userprofile-biography'},
                                mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True})}

