from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    (r'^starter/', TemplateView.as_view(template_name="foundation/starter.html")),
    url(r'', include('apps.web.urls')),
    (r'^accounts/', include('allauth.urls')),
    (r'^search/', include('haystack.urls')),
    (r'^api/', include('apps.api.routers')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
) 


# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns(
    '',
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),
)



urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns(
    '',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
            }),
    )
