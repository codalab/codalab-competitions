from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View, TemplateView, DetailView, ListView, FormView, UpdateView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import SingleObjectMixin
from django.template import RequestContext, loader
from django.forms.formsets import formset_factory
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

from apps.web import models
from apps.web import forms
from apps.web import tasks

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

def competition_index(request):
    template = loader.get_template("web/competitions/index.html")
    context = RequestContext(request, {
        'competitions' : models.Competition.objects.all(),
        })
    return HttpResponse(template.render(context))

@login_required
def my_index(request):
    template = loader.get_template("web/my/index.html")
    context = RequestContext(request, {
        'my_competitions' : models.Competition.objects.filter(creator=request.user),
        'competitions_im_in' : request.user.participation.all()
        })
    return HttpResponse(template.render(context))

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class CompetitionTabDetails(TemplateView):
    pass

class CompetitionCreate(CreateView):
    model = models.Competition
    template_name = 'web/my/create.html'
    form_class = forms.CompetitionForm

    def form_valid(self,form):
         form.instance.creator = self.request.user
         form.instance.modified_by = self.request.user
         return super(CompetitionCreate, self).form_valid(form)

    def form_invalid(self,form):
        raise Exception(form.errors)

    def get_success_url(self):
        return reverse('my_edit_competition', kwargs={'pk': self.object.pk})

class PhasesInline(InlineFormSet):
    model = models.CompetitionPhase

class CompetitionEdit(UpdateWithInlinesView):
    model = models.Competition
    inlines = [PhasesInline, ]
    template_name = 'web/competition/edit.html'
    
    def get_context_data(self, **kwargs):
        context = super(CompetitionEdit,self).get_context_data(**kwargs)
        return context

class CompetitionDelete(DeleteView):
    model = models.Competition
    # success_url = reverse_lazy('competition-list')
    template_name = 'web/competitions/confirm-delete.html'

class CompetitionDetailView(DetailView):
    queryset = models.Competition.objects.all()
    model = models.Competition

    def get_context_data(self, **kwargs):
        context = super(CompetitionDetailView,self).get_context_data(**kwargs)

        # This assumes the tabs were created in the correct order
        # TODO Add a rank, order by on ContentCategory
        side_tabs = dict()
        for category in models.ContentCategory.objects.all():
            pagecontent = context['object'].pagecontent
            if pagecontent is not None:
                tc = [x for x in pagecontent.pages.filter(category=category)]
            else:
                tc = []
            side_tabs[category] = tc 
        context['tabs'] = side_tabs
        submissions=dict()
        try:
            if self.request.user.is_authenticated() and self.request.user in [x.user for x in context['object'].participants.all()]:
                context['my_status'] = [x.status for x in context['object'].participants.all() if x.user == self.request.user][0].codename
                context['my_participant_id'] = context['object'].participants.get(user=self.request.user).id
                for phase in context['object'].phases.all():
                    submissions[phase] = models.CompetitionSubmission.objects.filter(participant=context['my_participant_id'], phase=phase)
                    if phase.is_active:
                        context['active_phase'] = phase
                        context['active_phase_submissions'] = submissions[phase]
                context['my_submissions'] = submissions
            else:
                context['my_status'] = "unknown"

        except ObjectDoesNotExist:
            pass

        return context

class CompetitionUpdate(UpdateView):
    model = models.Competition
    form_class = forms.CompetitionForm
        
class CompetitionPageDetails(TemplateView):
    pass
        
class CompetitionSubmissionsPage(TemplateView):
    pass

class CompetitionResultsPage(TemplateView):
    pass

class CompetitionDownloadDataset(TemplateView):
    pass

### Views for My Codalab

class MyIndex(LoginRequiredMixin):
    pass

class MyCreateCompetition(LoginRequiredMixin,TemplateView):
    
    template_name = 'web/my/create.html'
    
    def post(self,request,*args,**kwargs):
        c = models.Competition.objects.create(creator=request.user,
                                              title='Untitled',
                                              modified_by=request.user)
        cw = models.CompetitionWizard.objects.create(competition=c,
                                                     step=1,
                                                     creator=request.user)
        return HttpResponseRedirect(reverse('my_edit_competition',kwargs={'pk': c.pk}))
    
class MyEditCompetition(LoginRequiredMixin,TemplateView):
    template_name = 'web/my/edit.html'

    def post(self,request,competition_id=None):
        form = MyEditWizardForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('my_edit_competition', kwargs={'pk': form.cleaned_data['competition_id'] }))
        return HttpResponseBadRequest()
    
    def get_context_data(self, **kwargs):
        context = super(MyEditCompetition,self).get_context_data(**kwargs)
        comp = models.Competition.objects.get(pk=self.kwargs['pk'])
        context['competition'] = comp
        context['pages'] = comp.pagecontent.pages if comp.pagecontent else []
        #context['content'] = models.ContentContainer.objects.all()
        return context
 
class MyCompetitionParticipantView(LoginRequiredMixin,ListView):
    queryset = models.CompetitionParticipant.objects.all()
    template_name = 'web/my/participants.html'

    def get_context_data(self,**kwargs):
        ctx = super(MyCompetitionParticipantView,self).get_context_data(**kwargs)
        ctx['competition_id'] = self.kwargs.get('competition_id')
        return ctx

    def get_queryset(self):
        return self.queryset.filter(competition=self.kwargs.get('competition_id'))

## Partials

class CompetitionIndexPartial(TemplateView):
    
    def get_context_data(self,**kwargs):
        ## Currently gets all competitions
        context = super(CompetitionIndexPartial,self).get_context_data(**kwargs)
        per_page = self.request.GET.get('per_page',6)
        page = self.request.GET.get('page',1)
        clist = models.Competition.objects.all()
        
        pgn = Paginator(clist, per_page)
        try:
           competitions = pgn.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            competitions = pgn.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            competitions = []
        context['competitions'] = competitions
        return context

class MyCompetitionsManagedPartial(ListView):
    
    model = models.Competition
    template_name = 'web/my/_managed.html'
    queryset = models.Competition.objects.all()

    def get_queryset(self):
        return self.queryset.filter(creator=self.request.user)

class MyCompetitionsEnteredPartial(ListView):
    
    model = models.CompetitionParticipant
    template_name = 'web/my/_entered.html'
    queryset = models.CompetitionParticipant.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
        
class MyCompetitionDetailsTab(TemplateView):
    template_name = 'web/my/_tab.html'



# Bundle Views

class BundleListView(ListView):
    model = models.Bundle
    queryset = models.Bundle.objects.all()
  

class BundleCreateView(CreateView):
    model = models.Bundle
    action = "created"
    form_class = forms.BundleForm
  
    def form_valid(self, form):
        f = form.save(commit=False)
        f.save()
        tasks.create_directory.delay(f.id)
        return HttpResponseRedirect('/bundles')
  

class BundleDetailView(DetailView):
    model = models.Bundle

    def get_context_data(self, **kwargs):
        context = super(BundleDetailView, self).get_context_data(**kwargs)
        return context



# Bundle Run Views

class RunListView(ListView):
    model = models.Run
    queryset = models.Run.objects.all()
   
class RunCreateView(CreateView):
    model = models.Run
    action = "created"
    form_class = forms.RunForm
  
    def form_valid(self, form):
        f = form.save(commit=False)
        f.save()
        return HttpResponseRedirect('/runs')
  
  
class RunDetailView(DetailView):
    model = models.Run

    def get_context_data(self, **kwargs):
        context = super(RunDetailView, self).get_context_data(**kwargs)
        return context