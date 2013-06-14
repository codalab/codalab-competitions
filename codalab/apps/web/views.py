from django.views.generic import TemplateView

class AboutView(TemplateView):
    template = 'web/about.html'

class IndexView(TemplateView):
    template = 'web/index.html'

