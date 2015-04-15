import datetime
from django.db import models
from django.contrib.auth import get_user_model

from apps.web.models import Competition


User = get_user_model()


class Forum(models.Model):
    competition = models.OneToOneField(Competition, unique=True, related_name="forum")


class Thread(models.Model):
    forum = models.ForeignKey(Forum, related_name="threads")
    date_created = models.DateTimeField()
    started_by = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    last_post_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-last_post_date',)

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = datetime.datetime.today()
        return super(Thread, self).save(*args, **kwargs)


class Post(models.Model):
    thread = models.ForeignKey(Thread, related_name="posts")
    date_created = models.DateTimeField()
    posted_by = models.ForeignKey(User)
    content = models.TextField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = datetime.datetime.today()
        return super(Post, self).save(*args, **kwargs)
