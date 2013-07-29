from django.views.generic import View,TemplateView,DetailView,ListView,FormView,UpdateView,CreateView,DeleteView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import SingleObjectMixin
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from apps.web import models
from apps.web import forms

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

def get_content_context(typename=None):
    ## TODO: Add caching
    cont = {}
    ctx = {'content': cont}
    kw = {}
    if typename:
        kw['type__codename'] = typename          
    container = models.ContentContainer.objects.get(**kw)
    cont['container'] = container
    toplevel = []
    cont['toplevel'] = toplevel
    children = {}
    cont['children'] = children
    for e in sorted(container.entities.all(), key=lambda entity: entity.rank):
        if e.toplevel:
            toplevel.append(e)
        else:
            if e.parent_id not in children:
                children[e.codename] = []
            children[e.codename].append(e)
    return ctx


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
    template_name = 'web/my/edit2.html'
    
    def get_context_data(self, **kwargs):
        context = super(CompetitionEdit,self).get_context_data(**kwargs)
        # context['pages'] = .pagecontainer.pages
        # context.update(get_content_context(typename='competition_detail'))
        return context

class CompetitionDelete(DeleteView):
    queryset = models.Competition.objects.all()
    

    
class CompetitionDetailView(DetailView):
    queryset = models.Competition.objects.all()
    
    def get_context_data(self,**kwargs):
        context = super(CompetitionDetailView,self).get_context_data(**kwargs)
        cc = get_content_context(typename='competition_detail')
        
        context.update(cc)
        try:
            if self.request.user.is_authenticated():
                context['participation'] = self.request.user.participation.filter(competition=self.object)
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
    
    template_name = 'web/my/edit2.html'

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

class BundleView(TemplateView):
  model = models.Bundle
  template_name = 'web/bundle/index.html'
  
  def get_context_data(self, **kwargs):
    context = super(BundleView, self).get_context_data(**kwargs)
    context['bundle'] = Bundle.objects.get(pk=self.kwargs.get('bundle_id', None))
    return context
    
