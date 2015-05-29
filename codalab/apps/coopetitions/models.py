from django.db import models


class Like(models.Model):

    class Meta:
        unique_together = (('submission', 'user'),)

    submission = models.ForeignKey('web.CompetitionSubmission', related_name="likes")
    user = models.ForeignKey('authenz.ClUser')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s liked %s" % (self.user, self.submission)


class Dislike(models.Model):

    class Meta:
        unique_together = (('submission', 'user'),)

    submission = models.ForeignKey('web.CompetitionSubmission', related_name="dislikes")
    user = models.ForeignKey('authenz.ClUser')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s liked %s" % (self.user, self.submission)
