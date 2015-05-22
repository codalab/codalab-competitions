from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.sites.models import Site
from django.views.generic import TemplateView, RedirectView
from django.contrib import admin

from apps.web.models import Competition

from .. import views

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='web/index.html'), name='home'),
    url(r'^_ver', views.VersionView.as_view(),name='_version'),
    url(r'^my/', include('apps.web.urls.my')),
    url(r'^profile/(?P<pk>\d+)$', views.UserDetailView.as_view(), name='user_details'),
    url(r'^competitions/', include('apps.web.urls.competitions', namespace="competitions")),
    url(r'^worksheets/', include('apps.web.urls.worksheets')),
    url(r'^about/', TemplateView.as_view(template_name='web/help/about.html'), name='about'),
    url(r'^bundles/', include('apps.web.urls.bundles')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^health/', include('apps.health.urls')),
    url(r'^analytics/', include('apps.analytics.urls')),
    url(r'^forums/', include('apps.forums.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^coopetitions/', include('apps.coopetitions.urls', namespace="coopetitions")),

    # Direct URL redirects
    url(r'^(?i)AutoML/?', RedirectView.as_view(url='https://www.codalab.org/competitions/2321')),
    url(r'^(?i)ChalearnLAP_Pose/?', RedirectView.as_view(url='https://www.codalab.org/competitions/2231')),
    url(r'^(?i)ChalearnLAP_Action/?', RedirectView.as_view(url='https://www.codalab.org/competitions/2241')),
)


if settings.DEBUG:
    '''
    Debugging email templates
    '''
    class ExtraContextTemplateView(TemplateView):
        extra_context = None

        def get(self, request, *args, **kwargs):
            if request.GET.get('text', None) is not None:
                # Allow text emails with ?text=1 in the request
                self.template_name = self.template_name.replace('.html', '.txt')
            return super(ExtraContextTemplateView, self).get(request, *args, **kwargs)

        def get_context_data(self, *args, **kwargs):
            context = super(ExtraContextTemplateView, self).get_context_data(**kwargs)
            if self.extra_context:
                context.update(self.extra_context)
            return context

    urlpatterns += patterns('',
        (r'^email_view/organizer_to_participant/$', ExtraContextTemplateView.as_view(
            template_name='emails/notifications/participation_organizer_direct_email.html',
            extra_context={
                "body": "test",
                "competition": Competition.objects.all()[0] if len(Competition.objects.all()) > 0 else None,
                "site": Site.objects.get_current()
            }
        )),
        (r'^email_view/participation_requested/$', ExtraContextTemplateView.as_view(
            template_name='emails/notifications/participation_requested.html',
            extra_context={
                "competition": Competition.objects.all()[0] if len(Competition.objects.all()) > 0 else None,
                "site": Site.objects.get_current()
            }
        )),
        (r'^email_view/participation_revoked/$', ExtraContextTemplateView.as_view(
            template_name='emails/notifications/participation_revoked.html',
            extra_context={
                "competition": Competition.objects.all()[0] if len(Competition.objects.all()) > 0 else None,
                "site": Site.objects.get_current()
            }
        )),
        (r'^email_view/organizer_participation_requested/$', ExtraContextTemplateView.as_view(
            template_name='emails/notifications/organizer_participation_requested.html',
            extra_context={
                "competition": Competition.objects.all()[0] if len(Competition.objects.all()) > 0 else None,
                "site": Site.objects.get_current()
            }
        )),
        (r'^email_view/organizer_participation_revoked/$', ExtraContextTemplateView.as_view(
            template_name='emails/notifications/organizer_participation_revoked.html',
            extra_context={
                "competition": Competition.objects.all()[0] if len(Competition.objects.all()) > 0 else None,
                "site": Site.objects.get_current()
            }
        )),
    )

    '''
    Admin
    '''
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )
