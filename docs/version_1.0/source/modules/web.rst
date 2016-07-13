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
	:members:
	:exclude-members: HomePageView

	.. autoclass:: HomePageView()
		:exclude-members: get_context_data





