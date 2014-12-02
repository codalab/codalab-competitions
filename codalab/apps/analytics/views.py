import os

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from apps.web.models import Competition


User = get_user_model()


@login_required
def analytics_detail(request):
    if not request.user.is_staff:
        return HttpResponse(status=404)

    return render(request, "analytics/analytics.html", {
        'registered_user_count': User.objects.all().count(),
        'competition_count': Competition.objects.all().count(),
        'competitions_published_count': Competition.objects.filter(published=True).count(),
    })
