from django import forms
from django.forms.formsets import formset_factory
from django.contrib.auth import get_user_model
import models

User =  get_user_model()

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = models.Competition
        fields = ['title', 'description', 'image', 'has_registration', 'end_date', 'published']
        
class CompetitionPhaseForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionPhase
        fields = ['phasenumber', 'label', 'start_date', 'max_submissions', 'scoring_program', 'reference_data']

class CompetitionDatasetForm(forms.ModelForm):
    class Meta:
        model = models.Dataset

class CompetitionParticipantForm(forms.ModelForm):
    class Meta:
        model = models.CompetitionParticipant
