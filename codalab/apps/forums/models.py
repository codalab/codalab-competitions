import datetime

from django.core.urlresolvers import reverse
from django.db import models

from .helpers import send_mail


class Forum(models.Model):
    competition = models.OneToOneField('web.Competition', unique=True, related_name="forum")

    @classmethod
    def competition_post_save(cls, **kwargs):
        Forum.objects.create(competition=kwargs["instance"])


class Thread(models.Model):
    forum = models.ForeignKey('forums.Forum', related_name="threads")
    date_created = models.DateTimeField()
    started_by = models.ForeignKey('authenz.ClUser')
    title = models.CharField(max_length=255)
    last_post_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-last_post_date',)

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = datetime.datetime.today()
        return super(Thread, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum_thread_detail', kwargs={'forum_pk': self.forum.pk, 'thread_pk': self.pk })

    def notify_all_posters_of_new_post(self):
        users_in_thread = set(post.posted_by for post in self.posts.all())

        for user in users_in_thread:
            send_mail(
                context_data={
                    'thread': self,
                    'user': user,
                },
                subject='New post in %s' % self.title,
                html_file="forums/emails/new_post.html",
                text_file="forums/emails/new_post.txt",
                to_email=user.email
            )


class Post(models.Model):
    thread = models.ForeignKey('forums.Thread', related_name="posts")
    date_created = models.DateTimeField()
    posted_by = models.ForeignKey('authenz.ClUser')
    content = models.TextField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_created = datetime.datetime.today()
        return super(Post, self).save(*args, **kwargs)
