from django.forms import ModelForm

from .models import Queue


class QueueForm(ModelForm):

    class Meta:
        model = Queue
        fields = ('name', 'is_public', 'organizers')

    def __init__(self, *args, **kwargs):
        super(QueueForm, self).__init__(*args, **kwargs)

        # Remove extra help text that obfuscates our organizer message
        remove_message = 'Hold down "Control", or "Command" on a Mac, to select more than one.'
        self.fields['organizers'].help_text = self.fields['organizers'].help_text.replace(remove_message, '')


