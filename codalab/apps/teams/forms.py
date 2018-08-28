from django import forms
from django.forms.widgets import ClearableFileInput, Input, CheckboxInput
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from .models import Team, TeamMembership
from tinymce.widgets import TinyMCE
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
import os

class CustomImageField(ClearableFileInput):

    template_with_initial = '%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'
    template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

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
