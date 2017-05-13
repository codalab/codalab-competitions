from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import UpdateView

from .forms import ConfigurationForm
from .models import Configuration
from apps.web.models import Competition


class ConfigurationFormView(UpdateView):
    model = Configuration
    form_class = ConfigurationForm
    template_name = 'customizer/index.html'

    def get_object(self):
        # We're forcing the usage of only 1 configuration object here
        obj, created = Configuration.objects.get_or_create(pk=1)
        return obj

    def get_form(self, form_class):
        # Setup the form to be pre-filled with our admin user's competitions
        form = super(ConfigurationFormView, self).get_form(form_class)
        form.fields["only_competition"].queryset = Competition.objects.filter(
            creator=self.request.user,
        )
        return form

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        self.object = form.save()

        # We saved the new configuration but the settings may need to change
        settings.SINGLE_COMPETITION_VIEW_PK = self.object.only_competition.pk if self.object.only_competition else None
        settings.CUSTOM_HEADER_LOGO = self.object.header_logo.url

        return super(ConfigurationFormView, self).form_valid(form)
