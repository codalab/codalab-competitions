from django.shortcuts import render

from apps.jobs.models import Job
from apps.web import models as web_models


def health(request):
    jobs_in_queue_length = Job.objects.filter(status=Job.PENDING)


    return render(request, "health/health.html", {

    })
