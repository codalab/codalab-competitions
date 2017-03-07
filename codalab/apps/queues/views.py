from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import QueueForm
from .models import Queue


class RedirectToQueueListMixin(object):
    def get_success_url(self):
        return reverse('queues:list')


class QueueListView(LoginRequiredMixin, ListView):
    model = Queue
    template_name = 'queues/list.html'


class QueueCreateView(LoginRequiredMixin, RedirectToQueueListMixin, CreateView):
    model = Queue
    template_name = 'queues/form.html'
    form_class = QueueForm


class QueueUpdateView(LoginRequiredMixin, RedirectToQueueListMixin, UpdateView):
    model = Queue
    template_name = 'queues/form.html'
    form_class = QueueForm


class QueueDeleteView(LoginRequiredMixin, RedirectToQueueListMixin, DeleteView):
    model = Queue
    template_name = 'queues/delete.html'
