from django.forms import ModelForm
from .models import Configuration


class ConfigurationForm(ModelForm):
    class Meta:
        model = Configuration
        fields = ('header_logo', 'only_competition', 'front_page_message')

    def __init__(self, *args, **kwargs):
        super(ConfigurationForm, self).__init__(*args, **kwargs)

        self.fields['only_competition'].label_from_instance = self.competition_label_from_instance

    @staticmethod
    def competition_label_from_instance(competition):
        return "{} (id={})".format(competition, competition.pk)