from apps.api.views import competition_views as views
from apps.api.views import storage_views as storage_views
from apps.api.views import admin_views as admin_views
from django.conf.urls import url
from rest_framework import routers
from rest_framework.documentation import include_docs_urls


router = routers.DefaultRouter()


router.register(r'competition/(?P<competition_id>\d+)/participants', views.CompetitionParticipantAPIViewSet)
router.register(r'competition', views.CompetitionAPIViewSet)
router.register(r'competition/(?P<competition_id>\d+)/leaderboards', views.LeaderBoardViewSet)
router.register(r'defaultcontent', views.DefaultContentViewSet)

urlpatterns = router.urls

urlpatterns += (

    url(r'^competition/create$', views.CompetitionCreationApi.as_view(), name='api_competition_creation'),
    url(r'^competition/create/sas$', views.CompetitionCreationSasApi.as_view(), name='api_competition_creation_sas'),
    url(r'^competition/create/(?P<token>\d+)$', views.CompetitionCreationStatusApi.as_view(), name='api_competition_creation_status'),

    url(r'^competition/(?P<competition_id>\d+)/submission$', views.competition_submission_create, name='api_competition_submission_post'),
    url(r'^competition/(?P<competition_id>\d+)/submission/sas$', views.CompetitionSubmissionSasApi.as_view(), name='api_competition_submission_sas'),
    url(r'^competition/(?P<competition_id>\d+)/submission/(?P<pk>\d+)$', views.competition_submission_retrieve, name='api_competition_submission_get'),
    url(r'^competition/(?P<competition_id>\d+)/submission/(?P<pk>\d+)/leaderboard$', views.competition_submission_leaderboard, name='api_competition_submission_leaderboard'),
    url(r'^competition/(?P<competition_id>\d+)/submissions/?$', views.CompetitionSubmissionListViewSet.as_view({'get': 'list'}), name='api_competition_submission_list'),

    url(r'^competition/(?P<pk>\d+)/phases/(?P<phasenumber>\d+)$', views.competitionphase_retrieve, name='api_competitionphase'),
    url(r'^competition/(?P<competition_id>\d+)/phases/(?P<phase_id>\d+)/leaderboard$', views.leaderboard_retrieve, name='api_phase_leaderboard'),
    url(r'^competition/(?P<competition_id>\d+)/phases/(?P<phase_id>\d+)/leaderboard/data$', views.LeaderBoardDataViewSet.as_view(), name='api_phase_leaderboarddata'),

    url(r'^competition/(?P<pk>\d+)/phases/$', views.competitionphase_list, name='api_competitionphases_list'),

    url(r'^competition/(?P<competition_id>\d+)/pages/(?P<category>[a-zA-Z][\w\d\-\_]*)/$', views.competition_page_list, name='api_competition_page_list'),
    url(r'^competition/(?P<competition_id>\d+)/pages/(?P<pk>\d+)$', views.competition_page, name='api_competition_page'),
    url(r'^competition/(?P<competition_id>\d+)/pages/$', views.competition_page_list, name='api_competition_page_list'),
    url(r'^competition/(?P<pk>\d+)/pages/(?P<entity_label>\w[\w\d\-\_]+)/$', views.competition_page_list, name='api_competition_page_list'),
    # Chagrade specific features
    url(r'^submission/(?P<submission_id>\d+)/get_score', views.SubmissionScoreView.as_view(), name='submission_score'),
    url(r'^competition/(?P<competition_id>\d+)/enable_chagrade', views.AddChagradeBotView.as_view(), name='enable_chagrade'),
    # Storage Analytics
    url(r'^storage/analytics', storage_views.GetExistingStorageAnalytics.as_view(), name="existing_storage_analytics"),
    url(r'^storage/usage-history', storage_views.GetStorageUsageHistory.as_view(), name="storage_usage_history"),
    # Admin
    url(r'^admin/competitions/list', admin_views.GetCompetitions.as_view(), name="competitions"),
    url(r'^admin/competitions/update', admin_views.UpdateCompetitions.as_view(), name="update_competitions"),
    url(r'^admin/competition/(?P<competition_id>\d+)/apply_upper_bound_limit', admin_views.ApplyUpperBoundLimit.as_view(), name="apply_upper_bound_limit"),
    url(r'^admin/competitions/default_upper_bound_limit', admin_views.GetDefaultUpperBoundLimit.as_view(), name="get_default_upper_bound_limit"),
    # API Docs
    url(r'^docs/', include_docs_urls(title='Codalab API Reference', public=False))
)
