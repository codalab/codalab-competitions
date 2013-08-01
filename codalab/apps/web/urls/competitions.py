from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .. import views

partials_patterns = patterns('',
                             url(r'^indexpage$', views.CompetitionIndexPartial.as_view(template_name='web/competitions/_indexpage.html'),
                                 name='_competition_indexpage'),
                             )

urlpatterns = patterns('',
                       url(r'^$', views.competition_index, name='competitions'),
                       # url(r'^(?P<id>\d+)$', views.competition_view, name='competition_view'),
                       url(r'^(?P<pk>\d+)$', views.CompetitionDetailView.as_view(template_name='web/competitions/view.html'), name='competition_view'),
                       url(r'^_partials/', include(partials_patterns)),
                       url(r'^details/(?P<pk>\d+)$', views.CompetitionDetailView.as_view(template_name='web/competitions/details.html'),  name='competition_details'),
                       url(r'^details/(?P<id>\d+)/tab/(?P<tab_number>\d+)$',
                           views.CompetitionTabDetails.as_view(template_name='web/competitions/tab_details.html'), 
                           name='competition_page_tabs'),
                       url(r'^details/(?P<id>\d+)/page/(?P<page_number>\d+)$',
                           views.CompetitionPageDetails.as_view(template_name='web/competitions/page_details.html'), 
                           name='competition_page_details'),
                       url(r'^(?P<id>\d+)/submissions/(?P<phase>\d+)$',
                           views.CompetitionSubmissionsPage.as_view(template_name='web/competitions/submissions_page.html'), 
                           name='competition_submissions_page'),
                       url(r'^(?P<id>\d+)/results/(?P<phase>\d+)(?:\/(?P<score>\d+))?$',
                           views.CompetitionResultsPage.as_view(template_name='web/competitions/results_page.html'), 
                           name='competition_results_page'),
                       url(r'^(?P<id>\d+)/dataset/(?P<dataset_id>\d+)$',
                           views.CompetitionDownloadDataset.as_view(template_name='web/competitions/download_dataset.html'), 
                           name='competition_download_dataset'),
                       )

                        
