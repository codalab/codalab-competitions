from rest_framework import (permissions, status, views)
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

import logging

from django.db import transaction
from django.conf import settings

from apps.web.models import Competition, CompetitionPhase

logger = logging.getLogger(__name__)


@permission_classes((permissions.IsAuthenticated,))
class GetCompetitions(views.APIView):
    """
    Gets the competitions
    """
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        competitions = []
        for competition in list(Competition.objects.order_by('id').all()):
            competitions.append({
                'id': competition.id,
                'title': competition.title,
                'creator': competition.creator.username + " (" + competition.creator.email + ")",
                'start_date': competition.start_date,
                'end_date': competition.end_date,
                'upper_bound_max_submission_size': competition.upper_bound_max_submission_size,
                'max_submission_sizes': [phase.max_submission_size for phase in competition.phases.all().order_by('start_date')]
            })

        return Response(competitions, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class UpdateCompetitions(views.APIView):
    """
    Update competitions in batch
    body template:
    {
        competitions: [
            {
                id: 0,
                <attribute>: <value>
            }
        ]
    }
    """
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")
        
        competitions_to_update = request.data['competitions']
        if not competitions_to_update:
            return Response("No competitions to update", status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            for competition in competitions_to_update:
                try:
                    competition_in_db = Competition.objects.select_for_update().get(pk=competition['id'])
                    for attribute, value in competition.items():
                        if attribute != 'id':
                            logger.debug("Updating competition %d", competition_in_db.id)
                            setattr(competition_in_db, attribute, value)
                    competition_in_db.save()
                except Competition.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)

        ids = [comp['id'] for comp in competitions_to_update]
        competitions_updated = []
        for comp_id, competition in Competition.objects.in_bulk(ids).items():
            competitions_updated.append({
                'id': comp_id,
                'title': competition.title,
                'creator': competition.creator.username,
                'start_date': competition.start_date,
                'end_date': competition.end_date,
                'upper_bound_max_submission_size': competition.upper_bound_max_submission_size,
                'max_submission_sizes': [phase.max_submission_size for phase in competition.phases.all().order_by('start_date')]
            })

        return Response(competitions_updated, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class ApplyUpperBoundLimit(views.APIView):
    """
    Update the max submission size for all phases of the tompetition
    """
    def patch(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        competition_id = self.kwargs.get('competition_id')
        try:
            competition = Competition.objects.get(pk=competition_id)
        except Competition.DoesNotExist:
            return Response("Competition not found or is not accessible", status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            for phase in competition.phases.all().order_by('start_date'):
                try:
                    phase_in_db = CompetitionPhase.objects.select_for_update().get(pk=phase.id)
                    phase_in_db.max_submission_size = competition.upper_bound_max_submission_size
                    phase_in_db.save()
                except CompetitionPhase.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
        
        competition_updated_in_db = Competition.objects.get(pk=competition_id)
        competition_updated = {
            'id': competition_updated_in_db.id,
            'title': competition_updated_in_db.title,
            'creator': competition_updated_in_db.creator.username,
            'start_date': competition_updated_in_db.start_date,
            'end_date': competition_updated_in_db.end_date,
            'upper_bound_max_submission_size': competition_updated_in_db.upper_bound_max_submission_size,
            'max_submission_sizes': [phase.max_submission_size for phase in competition_updated_in_db.phases.all().order_by('start_date')]
        }
        return Response(competition_updated, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class GetDefaultUpperBoundLimit(views.APIView):
    """
    Gets the default upper bound max submission size
    """
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        default_upper_bound_max_submission_size = settings.DEFAULT_UPPER_BOUND_MAX_SUBMISSION_SIZE_MB

        return Response(default_upper_bound_max_submission_size, status=status.HTTP_200_OK)
