from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django_js_reverse.views import urls_js


from apps.web.views import MyAdminView

admin.autodiscover()

urlpatterns = [
    url(r'', include('apps.web.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^social/', include('social_django.urls', namespace='social')),
    url(r'^clients/', include('apps.authenz.urls')),
    url(r'^api/', include('apps.api.routers')),
    url(r'^search/', include('haystack.urls')),
    url(r'^admin_monitoring_links/$', MyAdminView.as_view(), name='admin_monitoring_links'),
    url(r'^teams/', include('apps.teams.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^hidden-admin/', include(admin.site.urls)),

    url(r'^', include('pin_passcode.urls')),

    # Switch User
    url(r"^su/", include("django_switchuser.urls")),
]

urlpatterns += [
    url(r'^jsreverse/$', urls_js, name='js_reverse')
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
