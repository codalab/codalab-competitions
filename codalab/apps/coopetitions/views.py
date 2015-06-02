from django.shortcuts import Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from apps.web.models import CompetitionSubmission

from .models import Like, Dislike


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
        # Remove dislike object if it exists, we should only be able to dislike OR like not both
        try:
            dislike = Dislike.objects.get(submission=submission, user=request.user)
            dislike.delete()
        except Dislike.DoesNotExist:
            pass

    # Force re-calculating of likes/dislikes
    submission.save()

    return HttpResponse(status=200, content=submission.get_overall_like_count())


@login_required
def dislike(request, submission_pk):
    '''Dislikes a submission or un-dislikes if they already disliked it'''
    try:
        submission = CompetitionSubmission.objects.get(pk=submission_pk)
    except CompetitionSubmission.DoesNotExist:
        raise Http404

    try:
        dislike = Dislike.objects.get(submission=submission, user=request.user)
        dislike.delete()
    except Dislike.DoesNotExist:
        Dislike.objects.create(submission=submission, user=request.user)
        # Remove like object if it exists, we should only be able to dislike OR like not both
        try:
            like = Like.objects.get(submission=submission, user=request.user)
            like.delete()
        except Like.DoesNotExist:
            pass

    # Force re-calculating of likes/dislikes
    submission.save()

    return HttpResponse(status=200, content=submission.get_overall_like_count())
