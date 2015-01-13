import os

from django import forms
from django.forms.formsets import formset_factory
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
import models
from tinymce.widgets import TinyMCE

User =  get_user_model()

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = models.Competition
        fields = (
            'title',
            'description',
            'disallow_leaderboard_modifying',
            'force_submission_to_leaderboard',
            'image',
            'has_registration',
            'end_date',
            'published',
            'enable_medical_image_viewer',
            'enable_detailed_results',
            'admins',
        )
        widgets = { 'description' : TinyMCE(attrs={'rows' : 20, 'class' : 'competition-editor-description'},
                                            mce_attrs={"theme" : "advanced", "cleanup_on_startup" : True, "theme_advanced_toolbar_location" : "top", "gecko_spellcheck" : True})}
    def __init__(self, *args, **kwargs):
        super(CompetitionForm, self).__init__(*args, **kwargs)
        self.fields["admins"].widget.attrs["style"] = "width: 100%;"

class CompetitionPhaseForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionPhase
        fields = (
            'phasenumber',
            'description',
            'label',
            'start_date',
            'max_submissions',
            'max_submissions_per_day',
            'execution_time_limit',
            'color',
            'is_scoring_only',
            'auto_migration',
            'leaderboard_management_mode',
            'input_data_organizer_dataset',
            'reference_data_organizer_dataset',
            'scoring_program_organizer_dataset',
        )
        widgets = {
            'leaderboard_management_mode' : forms.Select(
                attrs={'class': 'competition-editor-phase-leaderboard-mode'},
                choices=(('default', 'Default'), ('hide_results', 'Hide Results'))
            ),
            'DELETE' : forms.HiddenInput,
            'phasenumber': forms.HiddenInput
        }

    def clean_reference_data_organizer_dataset(self):
        # If no reference_data
        if not self.instance.reference_data and not self.cleaned_data["reference_data_organizer_dataset"]:
            raise forms.ValidationError("Phase has no reference_data set or chosen in the form, but it is required")

        # If we were using org dataset but do not select a new one
        if self.instance.reference_data_organizer_dataset and not self.cleaned_data["reference_data_organizer_dataset"]:
            raise forms.ValidationError("Phase has no reference_data set or chosen in the form, but it is required")

        return self.cleaned_data["reference_data_organizer_dataset"]

    def clean_scoring_program_organizer_dataset(self):
        # If no scoring_data
        if not self.instance.scoring_program and not self.cleaned_data["scoring_program_organizer_dataset"]:
            raise forms.ValidationError("Phase has no scoring_program set or chosen in the form, but it is required")

        # If we were using org dataset but do not select a new one
        if self.instance.scoring_program_organizer_dataset and not self.cleaned_data["scoring_program_organizer_dataset"]:
            raise forms.ValidationError("Phase has no scoring_program set or chosen in the form, but it is required")

        return self.cleaned_data["scoring_program_organizer_dataset"]


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
        fields = ["name", "description", "type", "data_file", "sub_data_files"]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user')
        super(OrganizerDataSetModelForm, self).__init__(*args, **kwargs)
        self.fields["sub_data_files"].widget.attrs["style"] = "width: 100%;"

        # If we have sub_data_files, then hide what is currently in data_file (which would be metadata containing references
        # to all of the sub_data_files)
        if self.instance.pk != None and self.instance.sub_data_files.count() > 0:
            self.fields["data_file"] = forms.FileField(initial=None, required=False)

    def clean_data_file(self):
        data = self.cleaned_data.get('data_file')

        #if data and self.data.get("sub_data_files"):
        #    raise forms.ValidationError("Cannot submit both single data file and multiple sub files!")
        #elif not data and not self.data.get("sub_data_files"):
        if not data and not self.data.get("sub_data_files"):
            raise forms.ValidationError("This field is required.")

        return data

    def save(self, commit=True):
        instance = super(OrganizerDataSetModelForm, self).save(commit=False)
        instance.uploaded_by = self.request_user

        # Write sub bundle metadata, replaces old data_file!
        if len(self.cleaned_data.get("sub_data_files")) > 0:
            lines = []

            for dataset in self.cleaned_data.get("sub_data_files"):
                file_name = os.path.splitext(os.path.basename(dataset.data_file.file.name))[0]
                lines.append("%s: %s" % (file_name, dataset.data_file.file.name))

            self.instance.data_file.save("metadata", ContentFile("\n".join(lines)))

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('participation_status_updates',
                  'organizer_status_updates',
                  'organizer_direct_message_updates',
                  'organization_or_affiliation',)
