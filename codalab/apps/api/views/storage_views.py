import datetime
from time import process_time
from json import dumps

from django.core import serializers
from django.conf import settings
from django.utils.dateparse import parse_datetime

from rest_framework import (permissions, status, viewsets, views, filters, mixins)
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import PermissionDenied, ParseError
from rest_framework.response import Response

from apps.authenz.models import ClUser
from apps.health.models import StorageDataPoint, CompetitionStorageDataPoint
from apps.web.models import Competition
from apps.web.utils import get_competition_size_data, BundleStorage, storage_recursive_find, storage_get_total_use


@permission_classes((permissions.IsAuthenticated,))
class GetStorageAnalyticTotalsView(views.APIView):
    """
    Gets total usage of bucket by looping through each key and adding the total size
    """
    def get(self, request, *args, **kwargs):
        print("##### STORAGE ANALYTICS --- get_total_analytics --- start")
        t = process_time()
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")
        total_bytes = storage_get_total_use(BundleStorage)
        data = {
            'total_bytes': total_bytes,
            'total_kilobytes': '{:.2f}'.format(total_bytes / 1000),
            'total_megabytes': '{:.2f}'.format(total_bytes / 1000 / 1000),
            'total_gigabytes': '{:.2f}'.format(total_bytes / 1000 / 1000 / 1000),
        }
        resp_status = status.HTTP_200_OK

        elapsed_time = process_time() - t
        print("##### STORAGE ANALYTICS --- get_total_analytics --- stop --- duration = {:.3f} seconds".format(elapsed_time))

        return Response(data, status=resp_status)

@permission_classes((permissions.IsAuthenticated,))
class GetExistingStorageAnalyticTotalsView(views.APIView):
    """
    Retrieve the last storage analytics total view results
    """
    def get(self, request, *args, **kwargs):
        print("##### STORAGE ANALYTICS --- new get_total_analytics --- start")
        t = process_time()
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")
        # total_bytes = storage_get_total_use(BundleStorage)
        last_storage_data_point = StorageDataPoint.objects.latest('id')
        print("last storage data point=", last_storage_data_point.total_use)
        data = {
            'created_at': last_storage_data_point.created,
            'total_use': last_storage_data_point.total_use,
            'competition_use': last_storage_data_point.competition_use,
            'submission_use': last_storage_data_point.submission_use,
            'dataset_use': last_storage_data_point.dataset_use,
            'bundle_use': last_storage_data_point.bundle_use,
            'dumps_use': last_storage_data_point.dumps_use,
        }
        resp_status = status.HTTP_200_OK

        elapsed_time = process_time() - t
        print("##### STORAGE ANALYTICS --- new get_total_analytics --- stop --- duration = {:.6f} seconds".format(elapsed_time))

        return Response(data, status=resp_status)


@permission_classes((permissions.IsAuthenticated,))
class GetCompetitionStorageAnalytics(views.APIView):
    """
    Gets storage use for competitions
    """
    def get(self, request, *args, **kwargs):
        print("##### STORAGE ANALYTICS --- get_competition_analytics --- start")
        t = process_time()
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        comp_list = []
        qs = Competition.objects.all().reverse()
        for comp in qs:
            comp_list.append(get_competition_size_data(comp))

        elapsed_time = process_time() - t
        print("##### STORAGE ANALYTICS --- get_competition_analytics --- stop --- duration = {:.3f} seconds".format(elapsed_time))

        return Response(comp_list, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class GetExistingCompetitionStorageAnalytics(views.APIView):
    """
    Retrieve the last storage analytics for competitions
    """
    def get(self, request, *args, **kwargs):
        print("##### STORAGE ANALYTICS --- new get_competition_analytics --- start")
        t = process_time()
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        data_points = []
        for c in list(CompetitionStorageDataPoint.objects.all()):
            di = {
                'id': c.competition_id,
                'title': c.title,
                'creator': c.creator,
                'is_active': c.is_active,
                'submissions': c.submissions,
                'datasets': c.datasets,
                'dumps': c.dumps,
                'bundle': c.bundle,
                'total': c.total
            }
            data_points.append(di)

        print(data_points)
        elapsed_time = process_time() - t
        print("##### STORAGE ANALYTICS --- get_competition_analytics --- stop --- duration = {:.3f} seconds".format(elapsed_time))

        return Response(data_points, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class GetUserStorageAnalytics(views.APIView):
    """
    Gets storage use for users
    """
    def get(self, request, *args, **kwargs):
        print("##### STORAGE ANALYTICS --- get_user_analytics --- start")
        t = process_time()
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        user_list = []
        qs = ClUser.objects.order_by('?').exclude(id=-1).exclude(username='AnonymousUser')
        for user in qs:
            user_list.append(user.get_storage_use_data())

        elapsed_time = process_time() - t
        print("##### STORAGE ANALYTICS --- get_user_analytics --- stop --- duration = {:.3f} seconds".format(elapsed_time))

        return Response(user_list, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated,))
class GetCompetitionStorageAnalyticsOverTime(views.APIView):
    """
    Gets storage use based off of timeframes. IE: Use at that current point in time.
    """

    unit_table = {
        'hours': ('hours', 1, "%H:%M:%S"),
        'days': ('days', 1, "%m/%d/%Y"),
        'weeks': ('weeks', 1, "%m/%d/%Y"),
        'months': ('weeks', 4, "%b"),
        'years': ('days', 365, "%Y")
    }

    def get(self, request, *args, **kwargs):
        print("##### STORAGE ANALYTICS --- get_analytics_overtime --- start")
        t = process_time()
        if not self.request.user.is_staff:
            raise PermissionDenied(detail="Admin only")

        unit_input = self.request.query_params.get('unit', 'years')
        sample_points = int(self.request.query_params.get('sample_points', 5))

        if not self.unit_table.get(unit_input, None):
            unit_input = 'years'

        unit, factor, date_format = self.unit_table[unit_input]
        data_list = []

        for index in range(0, sample_points):
            total = 0
            var_date = datetime.datetime.now() - datetime.timedelta(**{unit: factor*index})
            if settings.USE_AWS:
                bucket = BundleStorage.bucket
                for obj in bucket.objects.all():
                    # Returned time is in this format: 2020-10-13T20:15:50.000Z
                    if obj.last_modified.replace(tzinfo=None) <= var_date:
                        total += obj.size
            else:
                found_files = set(storage_recursive_find(BundleStorage))
                for file_path in found_files:
                    if BundleStorage.modified_time(file_path) <= var_date:
                        total += BundleStorage.size(file_path) or 0
            date_formatted = var_date.strftime(date_format)
            data_list.append({
                date_formatted: total
            })
        
        elapsed_time = process_time() - t
        print("##### STORAGE ANALYTICS --- get_analytics_overtime --- stop --- duration = {:.3f} seconds".format(elapsed_time))

        # Return the reverse of the list
        return Response(data_list[::-1], status=status.HTTP_200_OK)
