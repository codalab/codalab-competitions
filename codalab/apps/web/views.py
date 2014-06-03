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

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet, NamedFormsetsMixin
from extra_views import generic
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

def sort_data_table(request, context, list):
    context['order'] = order = request.GET.get('order') if 'order' in request.GET else 'id'
    context['direction'] = direction = request.GET.get('direction') if 'direction' in request.GET else 'asc'
    reverse = direction == 'desc'
    def sortkey(x):
        return x[order] if order in x and x[order] is not None else ''
    list.sort(key=sortkey, reverse=reverse)

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

class PagesInline(InlineFormSet):
    model = models.Page
    form_class = forms.PageForm
    extra = 0

class CompetitionUpload(LoginRequiredMixin, CreateView):
    model = models.CompetitionDefBundle
    template_name = 'web/competitions/upload_competition.html'

class CompetitionEdit(LoginRequiredMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    model = models.Competition
    form_class = forms.CompetitionForm
    inlines = [PagesInline, PhasesInline]
    inlines_names = ['Pages', 'Phases']
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

    @staticmethod
    def do_phase_migration(competition, current_phase, last_phase):
        '''
        Does the actual migrating of submissions from last_phase to current_phase

        competition: Competition model object
        current_phase: The new phase object we are entering
        last_phase: The phase object to transfer submissions from
        '''
        print 'do the thing'



        # get all items from last_phase

        #   should only get MOST RECENT submission made by participant

        #   create new submission object, only difference is phase
        #   add to current_phase
        #   call evaluate submission --------------- use API????

        # TODO: ONLY IF SUCCESSFUL
        competition.last_phase_migration = current_phase.phasenumber

    @staticmethod
    def check_trailing_phase_submissions(competition):
        '''
        Checks that the requested competition has all submissions in the current phase, none trailing in the previous
        phase

        competition: Normally we'd just get the object from context but just in case we want to use this from API as well,
        let's take a competition object
        '''
        last_phase = None
        current_phase = None

        for phase in competition.phases.all():
            if phase.is_active:
                current_phase = phase
                break

            last_phase = phase

        if current_phase.phasenumber > competition.last_phase_migration:
            CompetitionDetailView.do_phase_migration(competition, current_phase, last_phase)

    def get_context_data(self, **kwargs):
        context = super(CompetitionDetailView, self).get_context_data(**kwargs)
        competition = context['object']

        CompetitionDetailView.check_trailing_phase_submissions(competition)

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
        is_owner = self.request.user.id == competition.creator_id
        context['is_owner'] = is_owner
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
        context = super(MyCompetitionParticipantView, self).get_context_data(**kwargs)
        # create column definition
        columns = [
            {
                'label': 'NAME',
                'name': 'name'
            },
            {
                'label': 'EMAIL',
                'name': 'email'
            },
            {
                'label': 'STATUS',
                'name': 'status'
            },
            {
                'label': 'ENTRIES',
                'name': 'entries'
            }
        ]
        context['columns'] = columns
        # retrieve participant submissions information
        participant_list = []
        competition_participants = self.queryset.filter(competition=self.kwargs.get('competition_id'))
        competition_participants_ids = list(participant.id for participant in competition_participants)
        context['pending_participants'] = filter(lambda participant_submission: participant_submission.status.codename == models.ParticipantStatus.PENDING, competition_participants)
        participant_submissions = models.CompetitionSubmission.objects.filter(participant__in=competition_participants_ids)
        for participant in competition_participants:
            participant_entry = {
                'name': participant.user.username,
                'email': participant.user.email,
                'status': participant.status.codename,
                # equivalent to assigning participant.submissions.count() but without several multiple db queires
                'entries': len(filter(lambda participant_submission: participant_submission.participant.id == participant.id, participant_submissions))
            }
            participant_list.append(participant_entry)
        # order results
        sort_data_table(self.request, context, participant_list)
        context['participant_list'] = participant_list
        context['competition_id'] = self.kwargs.get('competition_id')
        return context

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
            file, file_type, file_name = submission.get_file_for_download(filetype, request.user)
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

class MyCompetitionSubmissionsPage(LoginRequiredMixin, TemplateView):
    # Serves the table of submissions in the submissions competition administration.
    # Requires an authenticated user who is an administrator of the competition.
    queryset = models.Competition.objects.all()
    model = models.Competition
    template_name = 'web/my/submissions.html'

    def get_context_data(self, **kwargs):
        phase_id = self.request.GET.get('phase');
        context = super(MyCompetitionSubmissionsPage, self).get_context_data(**kwargs)
        competition = models.Competition.objects.get(pk=self.kwargs['competition_id'])
        context['competition'] = competition
        if self.request.user.id == competition.creator_id:
            # find the active phase
            if (phase_id != None):
                context['selected_phase_id'] = int(phase_id)
                active_phase = competition.phases.filter(id=phase_id)[0]
            else:
                active_phase = competition.phases.all()[0]
                for phase in competition.phases.all():
                    if phase.is_active:
                        context['selected_phase_id'] = phase.id
                        active_phase = phase
            submissions = models.CompetitionSubmission.objects.filter(phase=active_phase)
            # find which submissions are in the leaderboard, if any and only if phase allows seeing results.
            id_of_submissions_in_leaderboard = [e.result.id for e in models.PhaseLeaderBoardEntry.objects.all() if e.result in submissions]
            # create column definition
            columns = [
                {
                    'label': 'SUBMITTED',
                    'name': 'submitted_at'
                },
                {
                    'label': 'SUBMITTED BY',
                    'name': 'submitted_by'
                },
                {
                    'label': 'FILENAME',
                    'name': 'filename'
                },
                {
                    'label': 'STATUS',
                    'name': 'status_name'
                },
                {
                    'label': 'LEADERBOARD',
                    'name': 'is_in_leaderboard'
                },
            ]
            scores = active_phase.scores()
            for score_group_index, score_group in enumerate(scores):
                column = {
                    'label': score_group['label'],
                    'name': 'score_' + str(score_group_index),
                }
                columns.append(column)
            # map submissions to view data
            submission_info_list = []
            for submission in submissions:
                submission_info = {
                    'id': submission.id,
                    'submitted_by': submission.participant.user.username,
                    'number': submission.submission_number,
                    'filename': submission.get_filename(),
                    'submitted_at': submission.submitted_at,
                    'status_name': submission.status.name,
                    'is_in_leaderboard': submission.id in id_of_submissions_in_leaderboard
                }
                # add score groups into data columns
                if (submission_info['is_in_leaderboard'] == True):
                    for score_group_index, score_group in enumerate(scores):
                        user_score = filter(lambda user_score: user_score[1]['username'] == submission.participant.user.username, score_group['scores'])[0]
                        main_score = filter(lambda main_score: main_score['name'] == score_group['selection_key'], user_score[1]['values'])[0]
                        submission_info['score_' + str(score_group_index)] = main_score['val']
                submission_info_list.append(submission_info)
            # order results
            sort_data_table(self.request, context, submission_info_list)
            # complete context
            context['columns'] = columns
            context['submission_info_list'] = submission_info_list
        return context

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
    template_name = 'web/bundles/index.html'
    def get_context_data(self, **kwargs):
        context = super(BundleListView, self).get_context_data(**kwargs)
        service = BundleService()
        results = service.items()
        context['bundles'] = results

        bundles = results
        items = []
        for bundle in bundles:
            item = {'uuid': bundle['uuid'],
                    'details_url': '/bundles/{0}'.format(bundle['uuid']),
                    'name': '',
                    'title': '<title not specified>',
                    'creator': '<creator not specified>',
                    'description': '<description not specified>'}
            if 'metadata' in bundle:
                metadata = bundle['metadata']
                for (key1, key2) in [('title', 'name'), ('creator', None), ('description', None)]:
                    if key2 is None:
                        key2 = key1
                    if key2 in metadata:
                        item[key1] = metadata[key2]
            items.append(item)
        context['items'] = items
        context['items_label'] = 'bundles'

        return context

class BundleDetailView(TemplateView):
    """
    Displays details for a bundle.
    """
    template_name = 'web/bundles/detail.html'
    def get_context_data(self, **kwargs):
        context = super(BundleDetailView, self).get_context_data(**kwargs)
        uuid = kwargs.get('uuid')
        service = BundleService()
        results = service.item(uuid)
        context['bundle'] = results
        return context

# Worksheets

class WorksheetListView(TemplateView):
    """
    Displays worksheets as a list.
    """
    template_name = 'web/worksheets/index.html'
    def get_context_data(self, **kwargs):
        context = super(WorksheetListView, self).get_context_data(**kwargs)
        return context

class WorksheetDetailView(TemplateView):
    """
    Displays details of a worksheet.
    """
    template_name = 'web/worksheets/detail.html'
    def get_context_data(self, **kwargs):
        context = super(WorksheetDetailView, self).get_context_data(**kwargs)
        return context
