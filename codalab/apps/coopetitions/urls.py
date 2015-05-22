from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^like/(?P<submission_pk>\d+)/', views.like, name='like'),
)
