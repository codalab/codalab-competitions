import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import DetailView, CreateView, DeleteView

from apps.web.views import LoginRequiredMixin
from .forms import PostForm, ThreadForm
from .models import Forum, Thread, Post


User = get_user_model()


class ForumBaseMixin(object):
    """
    Base Forum View. Inherited by other views.
    """

    def dispatch(self, *args, **kwargs):
        # Get object early so we can access it in multiple places
        self.forum = get_object_or_404(Forum, pk=self.kwargs['forum_pk'])
        if 'thread_pk' in self.kwargs:
            self.thread = get_object_or_404(Thread, pk=self.kwargs['thread_pk'])
        return super(ForumBaseMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ForumBaseMixin, self).get_context_data(**kwargs)
        context['forum'] = self.forum
        context['thread'] = self.thread if hasattr(self, 'thread') else None
        return context


class ForumDetailView(DetailView):
    """
    Shows the details of a particular Forum.
    """
    model = Forum
    template_name = "forums/thread_list.html"
    pk_url_kwarg = 'forum_pk'

    def get_context_data(self, **kwargs):
        context = super(ForumDetailView, self).get_context_data(**kwargs)
        context['thread_list_sorted'] = self.object.threads.order_by('pinned_date', '-date_created')\
            .select_related('forum', 'forum__competition', 'forum__competition__creator', 'started_by')\
            .prefetch_related('forum__competition__admins', 'posts')
        return context


class RedirectToThreadMixin(object):

    def get_success_url(self):
        return self.thread.get_absolute_url()


class CreatePostView(ForumBaseMixin, RedirectToThreadMixin, LoginRequiredMixin, CreateView):
    """
    View to create new post topics.
    """
    model = Post
    template_name = "forums/post_form.html"
    form_class = PostForm

    def form_valid(self, form):
        self.post = form.save(commit=False)
        self.post.thread = self.thread
        self.post.posted_by = self.request.user
        self.post.save()

        self.thread.last_post_date = datetime.datetime.now()
        self.thread.save()
        self.thread.notify_all_posters_of_new_post(self.post)
        return HttpResponseRedirect(self.get_success_url())


class DeletePostView(ForumBaseMixin, LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_pk'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.thread.forum.competition.creator == request.user or \
            request.user in self.object.thread.forum.competition.admins.all() or \
            self.object.posted_by == request.user:

            # If there are more posts in the thread, leave it around, otherwise delete it
            if self.object.thread.posts.count() == 1:
                success_url = self.object.thread.forum.get_absolute_url()
                self.object.thread.delete()
            else:
                success_url = self.object.thread.get_absolute_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            raise PermissionDenied("Cannot delete a post you don't own in a competition you aren't organizing!")


class CreateThreadView(ForumBaseMixin, RedirectToThreadMixin, LoginRequiredMixin, CreateView):
    """ View to post on current thread."""
    model = Thread
    template_name = "forums/post_form.html"
    form_class = ThreadForm

    def form_valid(self, form):
        self.thread = form.save(commit=False)
        self.thread.forum = self.forum
        self.thread.started_by = self.request.user
        self.thread.last_post_date = datetime.datetime.now()
        self.thread.save()

        # Make first post in the thread with the content
        Post.objects.create(thread=self.thread,
                            content=form.cleaned_data['content'],
                            posted_by=self.request.user)

        return HttpResponseRedirect(self.get_success_url())


class DeleteThreadView(ForumBaseMixin, LoginRequiredMixin, DeleteView):
    model = Thread
    pk_url_kwarg = 'thread_pk'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.forum.competition.creator == request.user or \
            request.user in self.object.forum.competition.admins.all() or \
            self.object.started_by == request.user:

            success_url = self.object.forum.get_absolute_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            raise PermissionDenied("Cannot delete a thread you don't own in a competition you aren't organizing!")


class ThreadDetailView(ForumBaseMixin, DetailView):
    """ View to read the details of a particular thread."""
    model = Thread
    template_name = "forums/thread_detail.html"
    pk_url_kwarg = 'thread_pk'

    def get_context_data(self, **kwargs):
        thread = self.object
        context = super(ThreadDetailView, self).get_context_data(**kwargs)
        context['ordered_posts'] = thread.posts.all().order_by('date_created')\
            .select_related('thread__forum__competition__creator', 'posted_by')\
            .prefetch_related('thread__forum__competition__admins')
        return context


@login_required
def pin_thread(request, thread_pk):
    try:
        thread = Thread.objects.get(pk=thread_pk)
    except Thread.DoesNotExist:
        raise Http404()

    if thread.forum.competition.creator == request.user or request.user in thread.forum.competition.admins.all():
        # Toggle pinned date on/off
        thread.pinned_date = now() if thread.pinned_date is None else None
        thread.save()
        return HttpResponseRedirect(thread.forum.get_absolute_url())
    else:
        raise PermissionDenied()
