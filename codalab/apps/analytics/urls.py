from django.conf.urls import patterns, include, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.analytics_detail, name='analytics_detail'),
)
