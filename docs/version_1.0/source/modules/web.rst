Web
======

Models
------
.. automodule:: apps.web.models
    :members:
    :exclude-members: ContentVisibility, ContentCategory, DefaultContentItem, ExternalFileType, ExternalFileSource, ParticipantStatus, Competition, Page, Dataset, _LeaderboardManagementMode, CompetitionPhase, CompetitionParticipant, CompetitionSubmissionStatus, CompetitionSubmission, SubmissionResultGroup, SubmissionResultGroupPhase, SubmissionScoreDef, CompetitionDefBundle, SubmissionScoreDefGroup, SubmissionComputedScore, SubmissionComputedScoreField, SubmissionScoreSet, SubmissionScore, PhaseLeaderBoard, PhaseLeaderBoardEntry, OrganizerDataSet, CompetitionSubmissionMetadata, PageContainer, ExternalFile

    .. autoclass:: ContentVisibility()
    .. autoclass:: ContentCategory()
    .. autoclass:: DefaultContentItem()
    .. autoclass:: PageContainer()
    .. autoclass:: ExternalFileType()
    .. autoclass:: ExternalFileSource()
    .. autoclass:: ParticipantStatus()
    .. autoclass:: Competition()
    	:members:
    	:exclude-members: save
    .. autoclass:: Page()
    .. autoclass:: Dataset()
    .. autoclass:: _LeaderboardManagementMode()
    	:members:
    	:exclude-members: DEFAULT, HIDE_RESULTS
    .. autoclass:: CompetitionPhase()
    	:members:
    	:exclude-members: rank_values

    	.. automethod:: rank_values()
    .. autoclass:: CompetitionParticipant()
    	:members:
    .. autoclass:: CompetitionSubmissionStatus()
    .. autoclass:: CompetitionSubmission()
    	:members:
    .. autoclass:: SubmissionResultGroup()
    .. autoclass:: SubmissionResultGroupPhase()
    	:exclude-members: save
    .. autoclass:: SubmissionScoreDef()
    .. autoclass:: CompetitionDefBundle()
    	:members:
    	:exclude-members: unpack

    	.. automethod:: unpack()
    .. autoclass:: CompetitionSubmissionMetadata()
    .. autoclass:: ExternalFile()

Views
-----
.. automodule:: apps.web.views

    .. autoclass:: CompetitionCheckMigrations()
    .. autoclass:: CompetitionCompleteResultsDownload()
    .. autoclass:: CompetitionDelete()
    .. autoclass:: CompetitionDetailView()
    .. autoclass:: CompetitionEdit()
        :members:
        :exclude-members: model
    .. autoclass:: CompetitionPublicSubmission()
    .. autoclass:: CompetitionPublicSubmissionByPhases()
    .. autoclass:: CompetitionResultsDownload()
    .. autoclass:: CompetitionResultsPage()
    .. autoclass:: CompetitionSubmissionsPage()
    .. autoclass:: HomePageView()
    .. autoclass:: MyCompetitionParticipantView()
    .. autoclass:: MyCompetitionSubmissionDetailedResults()
    .. autoclass:: MyCompetitionSubmissionOutput()
    .. autoclass:: MyCompetitionSubmissionsPage()
    .. autoclass:: UserDetailView()
    .. autoclass:: UserSettingsView()
    .. autofunction:: datasets_delete_multiple()
    .. autofunction:: download_dataset()
    .. autofunction:: download_competition_yaml()
    .. autofunction:: download_competition_bundle()
    .. autofunction:: download_leaderboard_results()
    .. autofunction:: submission_mark_as_failed()
    .. autofunction:: submission_migrate()
    .. autofunction:: submission_re_run()
    .. autofunction:: submission_toggle_leaderboard()
    .. autofunction:: submission_update_description()




















