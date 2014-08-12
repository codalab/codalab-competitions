import os

from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from apps.jobs.models import Job
from apps.web import models as web_models
from .models import HealthSettings


@login_required
def health(request):
    if not request.user.is_staff:
        return HttpResponse(status=404)

    jobs_pending = Job.objects.filter(status=Job.PENDING)
    jobs_pending_count = len(jobs_pending)

    jobs_finished_in_last_2_days = Job.objects.filter(status=Job.FINISHED, created__gt=datetime.now() - timedelta(days=2))
    jobs_finished_in_last_2_days_count = len(jobs_finished_in_last_2_days)
    jobs_finished_in_last_2_days_total_time_in_seconds = 0
    jobs_finished_in_last_2_days_avg = 0.0

    for job in jobs_finished_in_last_2_days:
        jobs_finished_in_last_2_days_total_time_in_seconds += (job.updated - job.created).seconds

    if jobs_finished_in_last_2_days_total_time_in_seconds > 0:
        jobs_finished_in_last_2_days_avg = jobs_finished_in_last_2_days_total_time_in_seconds / jobs_finished_in_last_2_days_count

    jobs_lasting_longer_than_10_minutes = []

    for job in jobs_pending:
        if (job.updated - job.created) > timedelta(minutes=10):
            jobs_lasting_longer_than_10_minutes.append(job)

    jobs_failed = Job.objects.filter(status=Job.FAILED)

    alert_emails = HealthSettings.objects.get_or_create(pk=1)[0].emails

    return render(request, "health/health.html", {
        "jobs_pending": jobs_pending,
        "jobs_pending_count": jobs_pending_count,
        "jobs_finished_in_last_2_days_avg": jobs_finished_in_last_2_days_avg,
        "jobs_lasting_longer_than_10_minutes": jobs_lasting_longer_than_10_minutes,
        "jobs_failed": jobs_failed,
        "jobs_failed_count": len(jobs_failed),
        "alert_emails": alert_emails,
    })


@login_required
def email_settings(request):
    if not request.user.is_staff or request.method != "POST":
        return HttpResponse(status=404)

    health_settings = HealthSettings.objects.get_or_create(pk=1)[0]
    health_settings.emails = request.POST.get("emails")
    health_settings.save()

    return HttpResponse()


def check_thresholds(request):
    # strip(",") and then trim() each!
    pass
