from django import forms
from django.forms.formsets import formset_factory
from django.contrib.auth import get_user_model
import models
from tinymce.widgets import TinyMCE

User =  get_user_model()

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = models.Competition
        fields = ('title', 'description', 'force_submission_to_leaderboard', 'image', 'has_registration', 'end_date', 'published')
        widgets = { 'description' : TinyMCE(attrs={'rows' : 20, 'class' : 'competition-editor-description'},
                                            mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True})}

class CompetitionPhaseForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionPhase
        fields = ('phasenumber', 'label', 'start_date', 'max_submissions', 'is_scoring_only', 'input_data', 'auto_migration', 'scoring_program', 'reference_data', 'leaderboard_management_mode')
        widgets = { 'leaderboard_management_mode' : forms.Select(attrs={'class': 'competition-editor-phase-leaderboard-mode'}, choices=(('default', 'Default'), ('hide_results', 'Hide Results'))),
                    'DELETE' : forms.HiddenInput, 'phasenumber': forms.HiddenInput }

class PageForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = ('category', 'rank', 'label', 'html', 'container')
        widgets = { 'html' : TinyMCE(attrs={'rows' : 20, 'class' : 'competition-editor-page-html'},
                                     mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True}),
                    'DELETE' : forms.HiddenInput, 'container' : forms.HiddenInput}

class CompetitionDatasetForm(forms.ModelForm):
    class Meta:
        model = models.Dataset

class CompetitionParticipantForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionParticipant


class OrganizerDataSetModelForm(forms.ModelForm):
    class Meta:
        model = models.OrganizerDataSet
        fields = ["name", "description", "type", "data_file"]

    def __init__(self, user=None, *args, **kwargs):
        self._user = kwargs.pop('user')

        super(OrganizerDataSetModelForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(OrganizerDataSetModelForm, self).save(commit=False)
        instance.uploaded_by = self._user
        if commit:
            instance.save()
            self.save_m2m()
        return instance
