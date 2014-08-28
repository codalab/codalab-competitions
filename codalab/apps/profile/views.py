from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse
from apps.authenz.models import ClUser
from apps.profile import forms
from apps.web import models as webModels
import time,datetime

@login_required
def profile(request):
    context = RequestContext(request)

    if request.method == 'POST':

        user_form = forms.UserForm(instance=request.user, data=request.POST)
        if hasattr(request.user, 'userprofile'):
            profile_form = forms.UserProfileForm(instance=request.user.userprofile, data=request.POST, files=request.FILES)
        else:
            profile_form = forms.UserProfileForm(data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()

            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            user_profile = profile_form.save(commit=False)
            user_profile.user = user
            user_profile.picture = profile_form.cleaned_data['picture']
            if request.FILES.has_key('picture'):
                ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
                request.FILES['picture'].name = user.username + '_' + ts + '.jpg'

            user_profile.save()

            # Update the profile form to see the picture
            profile_form = forms.UserProfileForm(instance=request.user.userprofile, data=request.POST, files=request.FILES)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print user_form.errors, profile_form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        user_form = forms.UserForm(instance=request.user)
        if hasattr(request.user, 'userprofile'):
            profile_form = forms.UserProfileForm(instance=request.user.userprofile)
        else:
            profile_form = forms.UserProfileForm()

    return render_to_response('profile.html', {'user_form': user_form, 'profile_form': profile_form, 'user': request.user}, context)

@login_required
def user_details(request, username):
    template = loader.get_template("user_details.html")
    if username=="":
        targetUser=request.user;
    else:
        targetUser=ClUser.objects.get(username=username);

    denied = webModels.ParticipantStatus.objects.get(codename=webModels.ParticipantStatus.DENIED)
    context = RequestContext(request, {
        'user': request.user,
        'target_user' : targetUser,
        'my_competitions' : webModels.Competition.objects.filter(creator=targetUser),
        'competitions_im_in' : targetUser.participation.all().exclude(status=denied),
        'showCompetitions' : True
    })
    return HttpResponse(template.render(context))
