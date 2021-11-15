from rest_framework import serializers
from apps.web import models as webmodels
import django_filters

class ContentCategorySerial(serializers.ModelSerializer):
    visibility = serializers.SlugField(source='visibility.codename')

    class Meta:
        model = webmodels.ContentCategory

class DefaultContentSerial(serializers.ModelSerializer):
    category_codename = serializers.SlugField(source='category.codename')
    category_name = serializers.CharField(source='category.name')
    initial_visibility = serializers.SlugField(source='initial_visibility.codename')
    class Meta:
        model = webmodels.DefaultContentItem


class PageContainerSerial(serializers.ModelSerializer):
    class Meta:
        model = webmodels.PageContainer
        fields = [
            'name',
            'object_id',
            'id',
        ]


class PageSerial(serializers.ModelSerializer):
    container = PageContainerSerial(read_only=True)
    class Meta:
        model = webmodels.Page
        fields = [
            'container',
            'codename',
            'title',
            'label',
            'markup',
            'html',
        ]


class CompetitionDatasetSerial(serializers.ModelSerializer):
    dataset_id = serializers.IntegerField()
    source_url = serializers.URLField()
    source_address_info = serializers.CharField()
    competition_id = serializers.IntegerField()
    phase_id = serializers.IntegerField()

    def validata_phase_id(self,attr,source):
        if not attr[source]:
            attr[source] = None
        return attr


class CompetitionParticipantSerial(serializers.ModelSerializer):
    class Meta:
        model = webmodels.CompetitionParticipant


class CompetitionSubmissionSerial(serializers.ModelSerializer):
    status = serializers.SlugField(source="status.codename", read_only=True)
    filename = serializers.ReadOnlyField(source="get_filename")

    class Meta:
        model = webmodels.CompetitionSubmission
        fields = ('id', 'status', 'status_details', 'submitted_at', 'submission_number', 'file', 'exception_details',
                  'description', 'method_name', 'method_description', 'project_url', 'publication_url', 'bibtex',
                  'organization_or_affiliation', 'filename')
        read_only_fields = (
            'participant', 'phase', 'id', 'status_details', 'submitted_at', 'submission_number', 'exception_details',
            'filename'
        )


class CompetitionSubmissionListSerializer(serializers.ModelSerializer):
    status = serializers.SlugField(source="status.codename", read_only=True)
    filename = serializers.SerializerMethodField()
    username = serializers.CharField(source='participant.user.username')
    leaderboard = serializers.SerializerMethodField()
    can_be_migrated = serializers.SerializerMethodField()
    participant_submission_number = serializers.CharField(read_only=True)
    phase_number = serializers.IntegerField(source='phase.phasenumber')
    size = serializers.SerializerMethodField()

    class Meta:
        model = webmodels.CompetitionSubmission
        fields = (
            'id',
            'status',
            'submission_number',
            'participant_submission_number',
            'phase',
            'phase_number',
            'submitted_at',
            'leaderboard',
            # 'results',
            'filename',
            'username',
            'is_migrated',
            'size',

            # Is it possible to migrate this to the next phase?
            'can_be_migrated',
        )

    def get_leaderboard(self, instance):
        return instance.id in self.context['leaderboard_submissions']

    def get_can_be_migrated(self, instance):
        return instance.id in self.context['migratable_submissions']

    def get_filename(self, instance):
        return instance.get_filename()

    def get_size(self, instance):
        return instance.size


class PhaseSerial(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = webmodels.CompetitionPhase
        fields = [
            'competition',
            'description',
            'phasenumber',
            'label',
            'start_date',
            'max_submissions',
            'max_submissions_per_day',
            'is_scoring_only',
            'datasets',
            'leaderboard_management_mode',
            'force_best_submission_to_leaderboard',
            'auto_migration',
            'is_migrated',
            'execution_time_limit',
            'color',
            'max_submission_size',
            'participant_max_storage_use',
            'delete_submissions_except_best_and_last',
            # 'input_data_organizer_dataset',
            # 'reference_data_organizer_dataset',
            # 'scoring_program_organizer_dataset',
            'phase_never_ends',
            'scoring_program_docker_image',
            'default_docker_image',
            'disable_custom_docker_image',
            # 'starting_kit_organizer_dataset',
            # 'public_data_organizer_dataset',
            # 'ingestion_program_organizer_dataset',
        ]
        read_only_fields = ['datasets']


class CompetitionPhaseSerial(serializers.ModelSerializer):
    end_date = serializers.DateTimeField(format='%Y-%m-%d')
    phases = PhaseSerial(many=True)

    class Meta:
        model = webmodels.Competition
        fields = ['end_date','phases']

class LeaderBoardSerial(serializers.ModelSerializer):
    entries =  CompetitionSubmissionSerial(read_only=True, source='submissions')
    class Meta:
        model = webmodels.PhaseLeaderBoard

class CompetitionDataSerial(serializers.ModelSerializer):
    image_url = serializers.URLField(source='image.url', read_only=True)
    phases = serializers.RelatedField(many=True, read_only=True)
    class Meta:
        model = webmodels.Competition


class PhaseRel(serializers.ModelSerializer):
    class Meta:
        model = webmodels.CompetitionPhase
        fields = [
            'description',
            'phasenumber',
            'label',
            'start_date',
            'max_submissions',
            'max_submissions_per_day',
            'is_scoring_only',
            'leaderboard_management_mode',
            'force_best_submission_to_leaderboard',
            'auto_migration',
            'execution_time_limit',
            'color',
            'phase_never_ends',
            'scoring_program_docker_image',
            # 'default_docker_image',
            'disable_custom_docker_image',
            # 'ingestion_program_docker_image',
        ]

class CompetitionSerial(serializers.ModelSerializer):
    phases = PhaseRel(many=True, read_only=True)
    # image_url = serializers.CharField(read_only=True)
    pages = PageSerial(many=True, read_only=True)

    class Meta:
        model = webmodels.Competition
        read_only_fields = ['image_url_base']
        # fields = '__all__'
        fields = [
            'title',
            'description',
            'url_redirect',
            'image',
            # 'image_url_base',
            'has_registration',
            'start_date',
            'end_date',
            'creator',
            'modified_by',
            'last_modified',
            'last_phase_migration',
            'is_migrating',
            'force_submission_to_leaderboard',
            'disallow_leaderboard_modifying',
            'enable_medical_image_viewer',
            'enable_detailed_results',
            'reward',
            'is_migrating_delayed',
            'allow_teams',
            'enable_per_submission_metadata',
            'allow_public_submissions',
            'enable_forum',
            'anonymous_leaderboard',
            'enable_teams',
            'require_team_approval',
            'hide_top_three',
            'hide_chart',
            'allow_organizer_teams',
            'deleted',
            'phases',
            'pages',
            'id'
        ]

class CompetitionFilter(django_filters.FilterSet):
    creator = django_filters.CharFilter(name="creator__username")
    class Meta:
        model = webmodels.Competition
        fields = ['creator']

class ScoreSerial(serializers.ModelSerializer):
    class Meta:
        model = webmodels.SubmissionScore

class CompetitionScoresSerial(serializers.ModelSerializer):
    competition_id = serializers.IntegerField(source='phase.competition.pk')
    phase_id = serializers.IntegerField(source='phase.pk')
    phasenumber = serializers.IntegerField(source='phase.pk')
    partitipant_id = serializers.IntegerField(source='participant.pk')
    status = serializers.CharField(source='status.codename')
    status_details = serializers.CharField(source='status_details')
    scores = ScoreSerial(read_only=True)

    class Meta:
        model = webmodels.CompetitionSubmission
