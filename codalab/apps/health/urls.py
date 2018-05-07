from django.conf.urls import patterns, include, url

from . import views


urlpatterns = patterns('',
    url(r'^status', views.health, name='health_status'),
    url(r'^email_settings', views.email_settings, name='health_status_email_settings'),
    url(r'^check_thresholds', views.check_thresholds, name='health_status_check_thresholds')
)
