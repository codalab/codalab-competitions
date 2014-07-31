from django.conf.urls import patterns, url
from apps.profile import views

urlpatterns = patterns('', url(r'^$', views.profile, name='profile'))