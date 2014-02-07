import datetime
import StringIO
import csv

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.views.generic import View, TemplateView, DetailView, ListView, FormView, UpdateView, CreateView, DeleteView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import SingleObjectMixin
from django.template import RequestContext, loader
from django.forms.formsets import formset_factory
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from apps.web import models
from apps.web import forms
from apps.web import tasks
from apps.web.bundles import BundleService

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

try:
    import azure
    import azure.storage
except ImportError:
    raise ImproperlyConfigured(
        "Could not load Azure bindings. "
        "See https://github.com/WindowsAzure/azure-sdk-for-python")

def competition_index(request):
    template = loader.get_template("web/competitions/index.html")
    context = RequestContext(request, {
        'competitions' : models.Competition.objects.filter(published=True),
        })
    return HttpResponse(template.render(context))

@login_required
def my_index(request):
    template = loader.get_template("web/my/index.html")
    denied = models.ParticipantStatus.objects.get(codename=models.ParticipantStatus.DENIED)
    context = RequestContext(request, {
        'my_competitions' : models.Competition.objects.filter(creator=request.user),
        'competitions_im_in' : request.user.participation.all().exclude(status=denied)
        })
    return HttpResponse(template.render(context))

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

#
# Competition Views
#

class PhasesInline(InlineFormSet):
    model = models.CompetitionPhase
    form_class = forms.CompetitionPhaseForm
    extra = 0

class CompetitionUpload(LoginRequiredMixin, CreateView):
    model = models.CompetitionDefBundle
    template_name = 'web/competitions/upload_competition.html'

class CompetitionEdit(LoginRequiredMixin, UpdateWithInlinesView):
    model = models.Competition
    form_class = forms.CompetitionForm
    inlines = [PhasesInline]
    template_name = 'web/competitions/edit.html'

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        return super(CompetitionEdit, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CompetitionEdit, self).get_context_data(**kwargs)
        return context

class CompetitionDelete(LoginRequiredMixin, DeleteView):
    model = models.Competition
    template_name = 'web/competitions/confirm-delete.html'
    success_url = '/my/#manage'
    
class CompetitionDetailView(DetailView):
    queryset = models.Competition.objects.all()
    model = models.Competition
    template_name = 'web/competitions/view.html'

    def get_context_data(self, **kwargs):
        context = super(CompetitionDetailView, self).get_context_data(**kwargs)
        competition = context['object']
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
        submissions = dict()
        all_submissions = dict()
        try:
            if self.request.user.is_authenticated() and self.request.user in [x.user for x in competition.participants.all()]:
                context['my_status'] = [x.status for x in competition.participants.all() if x.user == self.request.user][0].codename
                context['my_participant'] = competition.participants.get(user=self.request.user)
                for phase in competition.phases.all():
                    submissions[phase] = models.CompetitionSubmission.objects.filter(participant=context['my_participant'], phase=phase)
                    if phase.is_active:
                        context['active_phase'] = phase
                        context['my_active_phase_submissions'] = submissions[phase]
                context['my_submissions'] = submissions
            else:
                context['my_status'] = "unknown"
                for phase in competition.phases.all():
                    if phase.is_active:
                        context['active_phase'] = phase
                    all_submissions[phase] = phase.submissions.all()
                context['active_phase_submissions'] = all_submissions

        except ObjectDoesNotExist:
            pass

        return context     
 
class CompetitionSubmissionsPage(LoginRequiredMixin, TemplateView):
    # Serves the table of submissions in the Participate tab of a competition.
    # Requires an authenticated user who is an approved participant of the competition.
    template_name = 'web/competitions/_submit_results_page.html'

    def get_context_data(self, **kwargs):
        context = super(CompetitionSubmissionsPage, self).get_context_data(**kwargs)
        context['phase'] = None
        competition = models.Competition.objects.get(pk=self.kwargs['id'])
        if self.request.user in [x.user for x in competition.participants.all()]:
            participant = competition.participants.get(user=self.request.user)
            if participant.status.codename == models.ParticipantStatus.APPROVED:
                phase = competition.phases.get(pk=self.kwargs['phase'])
                submissions = models.CompetitionSubmission.objects.filter(participant=participant, phase=phase)
                # find which submission is in the leaderboard, if any and only if phase allows seeing results.
                id_of_submission_in_leaderboard = -1
                if not phase.is_blind:
                    ids = [e.result.id for e in models.PhaseLeaderBoardEntry.objects.filter(board__phase=phase)
                                       if e.result in submissions]
                    if len(ids) > 0: id_of_submission_in_leaderboard = ids[0]
                # map submissions to view data
                submission_info_list = []
                for submission in submissions:
                    submission_info = {
                        'id': submission.id,
                        'number': submission.submission_number,
                        'filename': submission.get_filename(),
                        'submitted_at': submission.submitted_at,
                        'status_name': submission.status.name,
                        'is_finished': submission.status.codename == 'finished',
                        'is_in_leaderboard': submission.id == id_of_submission_in_leaderboard
                    }
                    submission_info_list.append(submission_info)
                context['submission_info_list'] = submission_info_list
                context['phase'] = phase
        return context

class CompetitionResultsPage(TemplateView):
    # Serves the leaderboards in the Results tab of a competition.
    template_name = 'web/competitions/_results_page.html'
    def get_context_data(self, **kwargs):
        context = super(CompetitionResultsPage, self).get_context_data(**kwargs)
        competition = models.Competition.objects.get(pk=self.kwargs['id'])
        phase = competition.phases.get(pk=self.kwargs['phase'])
        context['phase'] = phase
        context['groups'] = phase.scores()
        return context

class CompetitionResultsDownload(View):

    def get(self, request, *args, **kwargs):
        competition = models.Competition.objects.get(pk=self.kwargs['id'])
        phase = competition.phases.get(pk=self.kwargs['phase'])
        if phase.is_blind:
            return HttpResponse(status=403)
        groups = phase.scores()

        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)

        for group in groups:
            csvwriter.writerow([group['label']])
            csvwriter.writerow([])
            
            headers = ["User"]
            sub_headers = [""]
            for header in group['headers']:
                subs = header['subs']
                if subs:
                    for sub in subs:
                        headers.append(header['label'])
                        sub_headers.append(sub['label'])
                else:
                    headers.append(header['label'])
            csvwriter.writerow(headers)
            csvwriter.writerow(sub_headers)

            if len(group['scores']) <= 0:
                csvwriter.writerow(["No data available"])
            else:
                for pk, scores in group['scores']:
                    row = [scores['username']]
                    for v in scores['values']:
                        if 'rnk' in v:
                            row.append("%s (%s)" % (v['val'], v['rnk']))
                        else:
                            row.append("%s (%s)" % (v['val'], v['hidden_rnk']))
                    csvwriter.writerow(row)

            csvwriter.writerow([])
            csvwriter.writerow([])
                    
        response = HttpResponse(csvfile.getvalue(), status=200, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=test.csv"

        return response

### Views for My Codalab

class MyIndex(LoginRequiredMixin):
    pass

class MyCompetitionParticipantView(LoginRequiredMixin, ListView):
    queryset = models.CompetitionParticipant.objects.all()
    template_name = 'web/my/participants.html'

    def get_context_data(self, **kwargs):
        ctx = super(MyCompetitionParticipantView, self).get_context_data(**kwargs)
        ctx['competition_id'] = self.kwargs.get('competition_id')
        return ctx

    def get_queryset(self):
        return self.queryset.filter(competition=self.kwargs.get('competition_id'))

## Partials

class CompetitionIndexPartial(TemplateView):
    
    def get_context_data(self, **kwargs):
        ## Currently gets all competitions
        context = super(CompetitionIndexPartial, self).get_context_data(**kwargs)
        per_page = self.request.GET.get('per_page', 6)
        page = self.request.GET.get('page', 1)
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

class MySubmissionResultsPartial(TemplateView):
    template_name = 'web/my/_submission_results.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(MySubmissionResultsPartial, self).get_context_data(**kwargs)

        participant_id = kwargs.get('participant_id')
        participant = models.CompetitionParticipant.objects.get(pk=participant_id)

        phase_id = kwargs.get('phase_id')
        phase = models.CompetitionPhase.objects.get(pk=phase_id)

        ctx['active_phase'] = phase
        ctx['my_active_phase_submissions'] = phase.submissions.filter(participant=participant)
        
        return ctx

class MyCompetitionSubmisisonOutput(LoginRequiredMixin, View):
    """
    This view serves the files associated with a submission.
    """
    def get(self, request, *args, **kwargs):
        submission = models.CompetitionSubmission.objects.get(pk=kwargs.get('submission_id'))
        filetype = kwargs.get('filetype')
        try:
            file, file_type, file_name = submission.get_file_for_download(filetype, request.user, False)
        except PermissionDenied:
            return HttpResponse(status=403)
        except ValueError:
            return HttpResponse(status=400)
        except:
            return HttpResponse(status=500)
        try:
            response = HttpResponse(file.read(), status=200, content_type=file_type)
            if file_type != 'text/plain':
                response['Content-Type'] = 'application/zip'
                response['Content-Disposition'] = 'attachment; filename="{0}"'.format(file_name)
            return response
        except azure.WindowsAzureMissingResourceError:
            # for stderr.txt which does not exist when no errors have occurred
            # this may hide a true 404 in unexpected circumstances
            return HttpResponse("", status=200, content_type='text/plain')
        except:
            msg = "There was an error retrieving file '%s'. Please try again later or report the issue."
            return HttpResponse(msg % filetype, status=200, content_type='text/plain')

class VersionView(TemplateView):
    template_name = 'web/project_version.html'

    def get_context_data(self):
        import subprocess
        p = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
        out, err = p.communicate()
        ctx = super(VersionView, self).get_context_data()
        ctx['commit_hash'] = out
        tasks.echo("version is " + out)
        return ctx

#
# Bundle Views
#

class BundleListView(TemplateView):
    """
    Displays the list of bundles.
    """
    template_name = 'web/bundles/bundle_list.html'
    def get_context_data(self, **kwargs):
        context = super(BundleListView, self).get_context_data(**kwargs)
        service = BundleService()
        results = service.items()
        context['bundles'] = results
        return context

class BundleDetailView(TemplateView):
    """
    Displays details for a bundle.
    """
    template_name = 'web/bundles/bundle_detail.html'
    def get_context_data(self, **kwargs):
        context = super(BundleDetailView, self).get_context_data(**kwargs)
        uuid = kwargs.get('uuid')
        service = BundleService()
        results = service.item(uuid)
        context['bundle'] = results
        return context
