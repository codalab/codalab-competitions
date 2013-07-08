from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from apps.web import views


partials_patterns = patterns(
    '',
    url(r'^_competitions_managed$', login_required(views.MyCompetitionsManagedPartial.as_view()),
        name='my_competitions_managed'),
    url(r'^_competitions_entered$', login_required(views.MyCompetitionsEnteredPartial.as_view()),
        name='my_competitions_entered'),
    )

urlpatterns = patterns(
    '',
    url(r'^$', login_required(TemplateView.as_view(template_name='web/my/index.html')), name='my_codalab'),
    url(r'^create_competition$', views.MyCreateCompetition.as_view(), name='my_create_competition'),
    url(r'^edit_competition/(?P<pk>\d+)$', views.MyEditCompetition.as_view(), name='my_edit_competition'),
    url(r'^_partials/', include(partials_patterns)),
    )
