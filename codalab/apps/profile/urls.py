from django.conf.urls import patterns, url
from apps.profile import views

urlpatterns = patterns('',
                       url(r'^my', views.profile, name='profile'),
                       url(r'^view/(?P<username>\w+)/$', views.user_details, name='details'))
