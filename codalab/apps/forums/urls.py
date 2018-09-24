from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^(?P<forum_pk>\d+)/$', views.ForumDetailView.as_view(), name='forum_detail'),
    url(r'^(?P<forum_pk>\d+)/new_thread/$', views.CreateThreadView.as_view(), name='forum_new_thread'),
    url(r'^(?P<forum_pk>\d+)/(?P<thread_pk>\d+)/$', views.ThreadDetailView.as_view(), name='forum_thread_detail'),
    url(r'^(?P<forum_pk>\d+)/(?P<thread_pk>\d+)/new_post/$', views.CreatePostView.as_view(), name='forum_new_post'),
    url(r'^(?P<forum_pk>\d+)/(?P<thread_pk>\d+)/delete/$', views.DeleteThreadView.as_view(), name='forum_delete_thread'),
    url(r'^(?P<forum_pk>\d+)/(?P<thread_pk>\d+)/delete/(?P<post_pk>\d+)/$', views.DeletePostView.as_view(), name='forum_delete_post'),
)
