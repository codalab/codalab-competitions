from django.forms import ModelForm
from . import models

class MyEditWizardForm(ModelForm):
    model = models.CompetitionWizardViewModel

    

    
