from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.ConfigurationFormView.as_view(), name='customize_codalab'),
)
