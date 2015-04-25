from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<forum_pk>\d+)/$', views.ForumDetailView.as_view(), name='forum_detail'),
    url(r'^(?P<forum_pk>\d+)/new_thread/$', views.CreateThreadView.as_view(), name='forum_new_thread'),
    url(r'^(?P<forum_pk>\d+)/(?P<thread_pk>\d+)/$', views.ThreadDetailView.as_view(), name='forum_thread_detail'),
    url(r'^(?P<forum_pk>\d+)/(?P<thread_pk>\d+)/new_post/$', views.CreatePostView.as_view(), name='forum_new_post'),
)
