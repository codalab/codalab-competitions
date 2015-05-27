from django.shortcuts import Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.web.models import CompetitionSubmission

from .models import Like


@login_required
def like(request, submission_pk):
    '''Likes a submission or unlikes if they already liked it'''
    try:
        submission = CompetitionSubmission.objects.get(pk=submission_pk)
    except CompetitionSubmission.DoesNotExist:
        raise Http404

    try:
        like = Like.objects.get(submission=submission, user=request.user)
        like.delete()
    except Like.DoesNotExist:
        Like.objects.create(submission=submission, user=request.user)

    return HttpResponse(status=200)
