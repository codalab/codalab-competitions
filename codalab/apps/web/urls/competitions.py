from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .. import views



urlpatterns = patterns('',
                       url(r'^$', views.competition_index, name='competitions'),
                       url(r'^(?P<pk>\d+)$', views.CompetitionDetailView.as_view(template_name='web/competitions/view.html'), name='competition_view'),
                       url(r'^(?P<id>\d+)/submissions/(?P<phase>\d+)$',
                           views.CompetitionSubmissionsPage.as_view(template_name='web/competitions/_submit_results_page.html'), 
                           name='competition_submissions_page'),
                       url(r'^(?P<id>\d+)/results/(?P<phase>\d+)$',
                           views.CompetitionResultsPage.as_view(template_name='web/competitions/_results_page.html'), 
                           name='competition_results_page')
                       )

                        
