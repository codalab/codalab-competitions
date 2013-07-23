from django import forms
from django.forms.formsets import formset_factory
from . import models

class SignupForm(forms.Form):
    
   first_name = forms.CharField(max_length=40, label='First Name')
   last_name = forms.CharField(max_length=40, label='Last Name')
   affiliation = forms.CharField(max_length=40, label='Affiliation')
   home_page = forms.URLField(max_length=40, label='Home Page')

   def save(self,user):
       user.first_name = self.cleaned_data['first_name']
       user.last_name = self.cleaned_data['last_name']
       user.affiliation = self.cleaned_data['affiliation']
       user.home_page = self.cleaned_data['home_page']
       user.save()


class CompetitionForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        self._user = kwargs.pop('user',None)
        super(CompetitionForm,self).__init__(*args,**kwargs)

    class Meta:
        model = models.Competition
        fields = ['title','description','has_registration','end_date']

class CompetitionPhaseForm(forms.ModelForm):

    class Meta:
        model = models.CompetitionPhase

    def save(self,commit=True):
        #self.request.FILES['dataset']
        # Possibly need async proccessing
        return super(CompetitionPhaseForm, self).save(commit)



class CompetitionParticipantForm(forms.ModelForm):
    
    class Meta:
        model = models.CompetitionParticipant

class CompetitionDatasetForm(forms.ModelForm):
    class Meta:
        model = models.Dataset




