import os

from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from apps.jobs.models import Job
from apps.web import models as web_models
from .models import HealthSettings


def get_health_metrics():
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

    jobs_failed = Job.objects.filter(status=Job.FAILED).order_by("-updated")

    health_settings = HealthSettings.objects.get_or_create(pk=1)[0]

    alert_emails = health_settings.emails if health_settings.emails else ""

    return {
        "jobs_pending": jobs_pending,
        "jobs_pending_count": jobs_pending_count,
        "jobs_finished_in_last_2_days_avg": jobs_finished_in_last_2_days_avg,
        "jobs_lasting_longer_than_10_minutes": jobs_lasting_longer_than_10_minutes,
        "jobs_failed": jobs_failed,
        "jobs_failed_count": len(jobs_failed),
        "alert_emails": alert_emails,
    }


@login_required
def health(request):
    if not request.user.is_staff:
        return HttpResponse(status=404)
    return render(request, "health/health.html", get_health_metrics())


@login_required
def email_settings(request):
    if not request.user.is_staff or request.method != "POST":
        return HttpResponse(status=404)
    health_settings = HealthSettings.objects.get_or_create(pk=1)[0]
    health_settings.emails = request.POST.get("emails")
    health_settings.save()
    return HttpResponse()


def check_thresholds(request):
    metrics = get_health_metrics()
    email_string = HealthSettings.objects.get_or_create(pk=1)[0].emails
    if email_string:
        emails = [s.strip() for s in email_string.split(",")]

        if metrics["jobs_pending_count"] > 100:
            send_mail("Codalab Warning: Jobs pending > 100!", "There are > 100 jobs pending for processing right now", settings.DEFAULT_FROM_EMAIL, emails)

        if metrics["jobs_lasting_longer_than_10_minutes"] and len(metrics["jobs_lasting_longer_than_10_minutes"]) > 10:
            send_mail("Codalab Warning: Many jobs taking > 10 minutes!", "There are many jobs taking longer than 10 minutes to process", settings.DEFAULT_FROM_EMAIL, emails)

    return HttpResponse()
