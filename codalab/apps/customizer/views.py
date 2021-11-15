from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from .forms import ConfigurationForm
from .models import Configuration


class ConfigurationFormView(UpdateView):
    model = Configuration
    form_class = ConfigurationForm
    template_name = 'customizer/index.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # Verify we are logged in and we have the appropriate permissions
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return super(ConfigurationFormView, self).dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()

    def get_object(self):
        # We're forcing the usage of only 1 configuration object here
        obj, created = Configuration.objects.get_or_create(pk=1)
        return obj

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        # We saved the new configuration but the settings may need to change
        settings.SINGLE_COMPETITION_VIEW_PK = form.instance.only_competition.pk if form.instance.only_competition else None
        settings.CUSTOM_HEADER_LOGO = form.instance.header_logo.url if form.instance.header_logo else None
        return super(ConfigurationFormView, self).form_valid(form)
