from django.conf.urls import url

from .views import newsletter_signup, newsletter_unsubscribe, newsletter_index, \
    newsletter_detail, newsletter_edit, newsletter_delete, newsletter_create

urlpatterns = [
    url(r'^signup/$', newsletter_signup, name='newsletter_signup'),
    url(r'^unsubscribe/$', newsletter_unsubscribe, name='newsletter_unsubscribe'),
    url(r'^edit/(?P<pk>\d+)/$', newsletter_edit, name='edit_newsletter'),
    url(r'^delete/(?P<pk>\d+)/$', newsletter_delete, name='delete_newsletter'),
    url(r'^detail/(?P<pk>\d+)/$', newsletter_detail, name='newsletter_detail'),
    url(r'^create/$', newsletter_create, name='create_newsletter'),
    url(r'^$', newsletter_index, name='newsletter_index'),
]
