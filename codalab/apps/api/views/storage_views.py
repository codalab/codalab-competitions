from django.conf import settings

from rest_framework import (permissions, status, viewsets, views, filters, mixins)
from rest_framework.decorators import action, link, permission_classes
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.response import Response

from apps.web.models import Competition
from apps.web.utils import get_competition_size, BundleStorage


@permission_classes((permissions.IsAuthenticated,))
class GetStorageAnalyticTotalsView(views.APIView):
    """
    Gets total usage of bucket by looping through each key and adding the total size
    """
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        if settings.USE_AWS:
            bucket = BundleStorage.bucket
            total_bytes = 0
            for key in bucket:
                total_bytes += key.size

            data = {
                'total_bytes': total_bytes,
                'total_kilobytes': total_bytes / 1000,
                'total_megabytes': total_bytes / 1000 / 1000,
                'total_gigabytes': total_bytes / 1000 / 1000 / 1000,
            }
            resp_status = status.HTTP_200_OK
        else:
            resp_status = status.HTTP_501_NOT_IMPLEMENTED
            data = {}

        return Response(data, status=resp_status)


@permission_classes((permissions.IsAuthenticated,))
class GetCompetitionStorageAnalytics(views.APIView):
    """
    Gets storage use for last 100 competitions
    """
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_staff or not self.request.user.is_superuser:
            raise PermissionDenied(detail="Admin only")

        comp_list = []
        qs = Competition.objects.all().reverse()[:100]
        for comp in qs:
            comp_list.append(get_competition_size(comp))

        return Response(comp_list, status=status.HTTP_200_OK)
