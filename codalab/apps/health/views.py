from apps.health.models import HealthSettings
from apps.jobs.models import Job
from apps.web.models import CompetitionSubmission
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

import csv

from .models import HealthSettings


def get_health_metrics():
    """
    Function that get health metrics based on the amouunt of jobs.

    :return: jobs dictionary
    -------
    - **Jobs pending** - Jobs pending queryset.
    - **Jobs pending count** - Length of pending jobs.
    - **Jobs finished in the last two days** - Jobs processed in the last two days.
    - **Jobs lasting longer than 10 minutes** - Jobs that are running for more than 30 minutes.
    - **Jobs failed** - Jobs that failed
    - **Jobs failed count** - Amount of jobs failed.
    - **alert emails** Email to send alert.
    - **alert_threshold** Threshold number.
    """
    jobs_pending = Job.objects.filter(status=Job.PENDING)

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

    jobs_failed = Job.objects.filter(status=Job.FAILED).order_by("-updated")[:10]

    health_settings = HealthSettings.objects.get_or_create(pk=1)[0]

    alert_emails = health_settings.emails if health_settings.emails else ""

    context = {
        "jobs_pending": jobs_pending,
        "jobs_pending_count": len(jobs_pending),
        "jobs_finished_in_last_2_days_avg": jobs_finished_in_last_2_days_avg,
        "jobs_lasting_longer_than_10_minutes": jobs_lasting_longer_than_10_minutes,
        "jobs_failed": jobs_failed,
        "jobs_failed_count": len(jobs_failed),
        "alert_emails": alert_emails,
        "alert_threshold": health_settings.threshold,
        "congestion_threshold": health_settings.congestion_threshold
    }

    # Health page update Dec 22, 2017

    # Today's jobs
    jobs_today = Job.objects.filter(created__year=datetime.today().year,
                                    created__day=datetime.today().day,
                                    created__month=datetime.today().month)
    jobs_today_failed = jobs_today.filter(status=Job.FAILED)
    jobs_today_finished = jobs_today.filter(status=Job.FINISHED)
    jobs_today_pending = jobs_today.filter(status=Job.PENDING)

    jobs_last_fifty = Job.objects.all().order_by('-created')[0:50]
    jobs_last_fifty_updated = Job.objects.all().order_by('-updated')[0:50]
    jobs_last_fifty_failed = Job.objects.filter(status=Job.FAILED).order_by('-updated')[0:50]

    jobs_pending_stuck = Job.objects.filter(status=Job.PENDING, created__lt=datetime.now() + timedelta(days=1)).order_by('-updated')[0:100]
    jobs_running_stuck = Job.objects.filter(status=Job.RUNNING, created__lt=datetime.now() + timedelta(days=1)).order_by('-updated')[0:100]

    context['jobs_today'] = jobs_today
    context['jobs_today_count'] = len(jobs_today)
    context['jobs_today_failed'] = jobs_today_failed
    context['jobs_today_failed_count'] = len(jobs_today_failed)
    context['jobs_today_finished'] = jobs_today_finished
    context['jobs_today_finished_count'] = len(jobs_today_finished)
    context['jobs_today_pending'] = jobs_today_pending
    context['jobs_today_pending_count'] = len(jobs_today_pending)

    context['jobs_last_fifty'] = jobs_last_fifty
    context['jobs_last_fifty_updated'] = jobs_last_fifty_updated
    context['jobs_last_fifty_failed'] = jobs_last_fifty_failed
    context['jobs_pending_stuck'] = jobs_pending_stuck
    context['jobs_pending_stuck_count'] = len(jobs_pending_stuck)
    context['jobs_running_stuck'] = jobs_running_stuck
    context['jobs_running_stuck_count'] = len(jobs_running_stuck)
    context['jobs_all_stuck_count'] = len(jobs_running_stuck) + len(jobs_pending_stuck)

    return context


@login_required
def health(request):
    if not request.user.is_staff:
        return HttpResponse(status=404)
    return render(request, "health/health.html", get_health_metrics())


@login_required
def simple_health(request):
    if not request.user.is_staff:
        return HttpResponse(status=404)
    qs = CompetitionSubmission.objects.all()
    qs = qs.filter(submitted_at__gte=datetime.now() - timedelta(days=10))
    qs = qs.order_by('-submitted_at')
    qs = qs.select_related('phase__competition')
    qs = qs.prefetch_related('phase', 'status', 'metadatas')

    submissions = qs[:250]

    return render(request, "health/simple_health.html", {
        "submissions": submissions,
    })


@login_required
def simple_health_csv(request):
    if not request.user.is_staff:
        return HttpResponse(status=404)
    qs = CompetitionSubmission.objects.all()
    qs = qs.filter(submitted_at__gte=datetime.now() - timedelta(days=2))
    qs = qs.order_by('-submitted_at')
    qs = qs.select_related('phase__competition')
    qs = qs.prefetch_related('phase', 'status', 'metadatas')

    submissions = qs[:250]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="health_simple_status.csv"'

    csvwriter = csv.writer(response)

    # Write our headers
    csvwriter.writerow([
        'Competition',
        'Competition End-Date',
        'Organizer',
        'Participant',
        'Submitted',
        'Size',
        'Status',
        'Hostnames',
        'Queue',
        'Run-Time',
    ])

    for sub in submissions:
        if sub.phase.competition.published:
            competition_info_string = '{0} - ({1})'
        else:
            competition_info_string = '{0} - ({1}?secret_key={2})'
        competition_info = competition_info_string.format(
            sub.phase.competition.title,
            reverse('competitions:view', kwargs={'pk': sub.phase.competition.pk}),
            sub.phase.competition.secret_key
        )
        csvwriter.writerow([
            competition_info,
            sub.phase.competition.end_date.isoformat() if sub.phase.competition.end_date else '',
            '{0} ({1})'.format(sub.phase.competition.creator.username, sub.phase.competition.creator.email),
            '{0} ({1})'.format(sub.participant.user.username, sub.participant.user.email),
            timezone.now() - sub.submitted_at,
            sub.size,
            sub.status.codename,
            [metadata.hostname for metadata in sub.metadatas.all() if metadata.hostname] or 'No data!',
            sub.phase.competition.queue if sub.phase.competition.queue and sub.phase.competition.queue != '' else '*',
            sub.run_time if sub.run_time else '',
        ])
    return response



@login_required
def storage_analytics(request):
    if not request.user.is_staff:
        return HttpResponse(status=403)
    return render(request, "health/storage.html")


@login_required
def email_settings(request):
    if not request.user.is_staff or request.method != "POST":
        return HttpResponse(status=404)
    health_settings = HealthSettings.objects.get_or_create(pk=1)[0]
    health_settings.emails = request.POST.get("emails")
    health_settings.threshold = request.POST.get("alert_threshold")
    health_settings.congestion_threshold = request.POST.get("congestion_threshold")
    health_settings.save()
    return HttpResponse()


def check_thresholds(request):
    """
    Function that checks if the amount of pending jobs is greater than threshold number.
    It will send an email if the number exceeded.
    """
    metrics = get_health_metrics()
    health_settings = HealthSettings.objects.get_or_create(pk=1)[0]
    email_string = health_settings.emails
    if email_string:
        emails = [s.strip() for s in email_string.split(",")]

        if metrics["jobs_pending_count"] > health_settings.threshold:
            send_mail(
                "Codalab Warning: Jobs pending > %s!" % health_settings.threshold,
                "There are > %s jobs pending for processing right now" % health_settings.threshold,
                settings.DEFAULT_FROM_EMAIL,
                emails
            )

        if metrics["jobs_lasting_longer_than_10_minutes"] and len(metrics["jobs_lasting_longer_than_10_minutes"]) > 10:
            send_mail("Codalab Warning: Many jobs taking > 10 minutes!", "There are many jobs taking longer than 10 minutes to process", settings.DEFAULT_FROM_EMAIL, emails)

    return HttpResponse()
