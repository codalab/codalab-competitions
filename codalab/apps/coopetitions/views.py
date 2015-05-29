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
        submission.like_count -= 1
        submission.save()
    except Like.DoesNotExist:
        Like.objects.create(submission=submission, user=request.user)
        submission.like_count += 1
        submission.save()
        # Remove dislike object if it exists, we should only be able to dislike OR like not both
        try:
            dislike = Dislike.objects.get(submission=submission, user=request.user)
            dislike.delete()
        except Dislike.DoesNotExist:
            pass

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
        submission.dislike_count -= 1
        submission.save()
    except Dislike.DoesNotExist:
        Dislike.objects.create(submission=submission, user=request.user)
        submission.dislike_count += 1
        submission.save()
        # Remove like object if it exists, we should only be able to dislike OR like not both
        try:
            like = Like.objects.get(submission=submission, user=request.user)
            like.delete()
        except Like.DoesNotExist:
            pass

    return HttpResponse(status=200, content=submission.get_overall_like_count())
