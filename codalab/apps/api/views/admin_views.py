from rest_framework import (permissions, status, views)
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

import logging

from django.db import transaction

from apps.web.models import Competition

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
                'upper_bound_max_submission_size': competition.upper_bound_max_submission_size
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
                'upper_bound_max_submission_size': competition.upper_bound_max_submission_size
            })

        return Response(competitions_updated, status=status.HTTP_200_OK)
