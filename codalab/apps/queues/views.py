from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import QueueForm
from .models import Queue
from . import rabbit


class RedirectToQueueListMixin(object):
    def get_success_url(self):
        return reverse('queues:list')


class QueueListView(LoginRequiredMixin, ListView):
    model = Queue
    template_name = 'queues/list.html'

    def get_queryset(self):
        return Queue.objects.filter(owner=self.request.user)


class QueueCreateView(LoginRequiredMixin, RedirectToQueueListMixin, CreateView):
    model = Queue
    template_name = 'queues/form.html'
    form_class = QueueForm

    def form_valid(self, form):
        queue = form.save(commit=False)
        queue.owner = self.request.user

        try:
            if rabbit.check_user_needs_initialization(self.request.user):
                rabbit.initialize_user(self.request.user)
            queue.vhost = rabbit.create_queue(self.request.user)

            # Only save queue if things were successful
            queue.save()
            return HttpResponseRedirect(self.get_success_url())
        except:
            raise
            return HttpResponse("Failed to create RabbitMQ queue... please report the issue on the Codalab github!")


class QueueUpdateView(LoginRequiredMixin, RedirectToQueueListMixin, UpdateView):
    model = Queue
    template_name = 'queues/form.html'
    form_class = QueueForm


class QueueDeleteView(LoginRequiredMixin, RedirectToQueueListMixin, DeleteView):
    model = Queue
    template_name = 'queues/delete.html'

    def delete(self, request, *args, **kwargs):
        queue = self.get_object()
        if request.user != queue.owner:
            raise PermissionDenied("Cannot delete this queue, you don't own it.")
        success_url = self.get_success_url()
        queue.delete()
        return HttpResponseRedirect(success_url)
